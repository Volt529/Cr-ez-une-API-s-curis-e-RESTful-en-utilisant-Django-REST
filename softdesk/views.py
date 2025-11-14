from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from .models import User, Project, Contributor, Issue, Comment
from .serializers import (
    UserSerializer, UserDetailSerializer, ProjectSerializer,
    ContributorSerializer, IssueSerializer, CommentSerializer
)
from .permissions import (
    IsAuthorOrReadOnly, IsProjectContributor, 
    IsProjectAuthor, IsAuthorOrProjectAuthor
)


class StandardResultsSetPagination(PageNumberPagination):
    """Pagination standard pour toutes les listes (Green Code)"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des utilisateurs.
    Inscription libre, mais seul l'utilisateur peut voir/modifier son profil.
    """
    queryset = User.objects.all()
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return UserSerializer
        return UserDetailSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        # Un utilisateur ne peut voir que son propre profil (RGPD)
        if self.request.user.is_authenticated:
            return User.objects.filter(id=self.request.user.id)
        return User.objects.none()

    def destroy(self, request, *args, **kwargs):
        # Droit à l'oubli (RGPD)
        instance = self.get_object()
        if instance != request.user:
            return Response(
                {"detail": "Vous ne pouvez supprimer que votre propre compte."},
                status=status.HTTP_403_FORBIDDEN
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des projets.
    Seuls les contributeurs peuvent accéder aux projets.
    """
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsProjectContributor, IsAuthorOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # Retourner uniquement les projets dont l'utilisateur est contributeur
        return Project.objects.filter(
            contributors__user=self.request.user
        ).distinct()

    @action(detail=True, methods=['get'], url_path='contributors')
    def list_contributors(self, request, pk=None):
        """Liste les contributeurs d'un projet"""
        project = self.get_object()
        contributors = project.contributors.all()
        serializer = ContributorSerializer(contributors, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='add-contributor', 
            permission_classes=[IsAuthenticated, IsProjectAuthor])
    def add_contributor(self, request, pk=None):
        """Ajoute un contributeur au projet (réservé à l'auteur)"""
        project = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "Utilisateur non trouvé."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if Contributor.objects.filter(user=user, project=project).exists():
            return Response(
                {"detail": "Cet utilisateur est déjà contributeur."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        contributor = Contributor.objects.create(user=user, project=project)
        serializer = ContributorSerializer(contributor)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='contributors/(?P<contributor_id>[^/.]+)',
            permission_classes=[IsAuthenticated, IsProjectAuthor])
    def remove_contributor(self, request, pk=None, contributor_id=None):
        """Retire un contributeur du projet (réservé à l'auteur)"""
        project = self.get_object()
        contributor = get_object_or_404(Contributor, id=contributor_id, project=project)
        
        if contributor.user == project.author:
            return Response(
                {"detail": "Impossible de retirer l'auteur du projet."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        contributor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IssueViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des issues.
    Accessible uniquement aux contributeurs du projet.
    """
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated, IsProjectContributor, IsAuthorOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # Filtrer par projet si fourni dans l'URL
        project_id = self.kwargs.get('project_pk')
        if project_id:
            # Vérifier que l'utilisateur est contributeur
            if not Contributor.objects.filter(
                user=self.request.user, 
                project_id=project_id
            ).exists():
                return Issue.objects.none()
            return Issue.objects.filter(project_id=project_id)
        
        # Sinon, retourner toutes les issues des projets contributés
        return Issue.objects.filter(
            project__contributors__user=self.request.user
        ).distinct()

    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_pk')
        if project_id:
            # Vérifier que l'utilisateur est contributeur
            if not Contributor.objects.filter(
                user=self.request.user,
                project_id=project_id
            ).exists():
                raise PermissionError("Vous devez être contributeur du projet.")
            serializer.save(project_id=project_id)
        else:
            serializer.save()


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des commentaires.
    Accessible uniquement aux contributeurs du projet.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsProjectContributor, IsAuthorOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # Filtrer par issue si fourni dans l'URL
        issue_id = self.kwargs.get('issue_pk')
        if issue_id:
            issue = get_object_or_404(Issue, id=issue_id)
            # Vérifier que l'utilisateur est contributeur du projet
            if not Contributor.objects.filter(
                user=self.request.user,
                project=issue.project
            ).exists():
                return Comment.objects.none()
            return Comment.objects.filter(issue_id=issue_id)
        
        # Sinon, retourner tous les commentaires des projets contributés
        return Comment.objects.filter(
            issue__project__contributors__user=self.request.user
        ).distinct()

    def perform_create(self, serializer):
        issue_id = self.kwargs.get('issue_pk')
        if issue_id:
            issue = get_object_or_404(Issue, id=issue_id)
            # Vérifier que l'utilisateur est contributeur
            if not Contributor.objects.filter(
                user=self.request.user,
                project=issue.project
            ).exists():
                raise PermissionError("Vous devez être contributeur du projet.")
            serializer.save(issue=issue)
        else:
            serializer.save()


class ContributorViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des contributeurs.
    Seul l'auteur du projet peut gérer les contributeurs.
    """
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated, IsProjectContributor, IsAuthorOrProjectAuthor]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        if project_id:
            # Vérifier que l'utilisateur est contributeur du projet
            if not Contributor.objects.filter(
                user=self.request.user,
                project_id=project_id
            ).exists():
                return Contributor.objects.none()
            return Contributor.objects.filter(project_id=project_id)
        return Contributor.objects.none()