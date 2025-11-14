from rest_framework import permissions
from .models import Contributor


class IsAuthenticated(permissions.BasePermission):
    """Seuls les utilisateurs authentifiés peuvent accéder"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée : seul l'auteur peut modifier/supprimer.
    Les autres peuvent lire (si contributeurs).
    """
    def has_object_permission(self, request, view, obj):
        # Lecture autorisée pour tous les contributeurs
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Modification/suppression uniquement pour l'auteur
        return obj.author == request.user


class IsProjectContributor(permissions.BasePermission):
    """
    Vérifie que l'utilisateur est contributeur du projet.
    Pour les vues de Project, Issue, et Comment.
    """
    def has_permission(self, request, view):
        # Pour la création, vérifier dans la vue
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Déterminer le projet selon le type d'objet
        if hasattr(obj, 'project'):
            project = obj.project
        elif obj.__class__.__name__ == 'Project':
            project = obj
        elif hasattr(obj, 'issue'):
            project = obj.issue.project
        else:
            return False

        # Vérifier que l'utilisateur est contributeur
        return Contributor.objects.filter(
            user=request.user,
            project=project
        ).exists()


class IsProjectAuthor(permissions.BasePermission):
    """
    Seul l'auteur du projet peut ajouter/retirer des contributeurs.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # obj est le Project
        return obj.author == request.user


class IsAuthorOrProjectAuthor(permissions.BasePermission):
    """
    L'auteur du projet ou l'auteur de la ressource peut modifier/supprimer.
    Utilisé pour les Contributors.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Le créateur du projet peut gérer les contributeurs
        if hasattr(obj, 'project'):
            return obj.project.author == request.user
        
        return False