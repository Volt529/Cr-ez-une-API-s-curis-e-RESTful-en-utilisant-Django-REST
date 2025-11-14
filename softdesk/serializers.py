from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Project, Contributor, Issue, Comment


class UserSerializer(serializers.ModelSerializer):
    """Serializer pour l'utilisateur"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password2', 'age', 
                  'can_be_contacted', 'can_data_be_shared', 'created_time']
        read_only_fields = ['id', 'created_time']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        
        # Vérifier que l'âge est fourni
        if 'age' not in attrs or attrs['age'] is None:
            raise serializers.ValidationError({"age": "L'âge est obligatoire."})
        
        if attrs['age'] < 15:
            raise serializers.ValidationError({"age": "Vous devez avoir au moins 15 ans (RGPD)."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer pour les détails de l'utilisateur (sans mot de passe)"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'age', 'can_be_contacted', 
                  'can_data_be_shared', 'created_time']
        read_only_fields = ['id', 'created_time']


class ContributorSerializer(serializers.ModelSerializer):
    """Serializer pour les contributeurs"""
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Contributor
        fields = ['id', 'user', 'user_username', 'project', 'created_time']
        read_only_fields = ['id', 'created_time']

    def validate(self, attrs):
        # Vérifier que l'utilisateur n'est pas déjà contributeur
        if Contributor.objects.filter(user=attrs['user'], project=attrs['project']).exists():
            raise serializers.ValidationError("Cet utilisateur est déjà contributeur de ce projet.")
        return attrs


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer pour les projets"""
    author_username = serializers.CharField(source='author.username', read_only=True)
    contributors_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'type', 'author', 'author_username', 
                  'contributors_count', 'created_time']
        read_only_fields = ['id', 'author', 'created_time']

    def get_contributors_count(self, obj):
        return obj.contributors.count()

    def create(self, validated_data):
        # L'auteur devient automatiquement contributeur
        request = self.context.get('request')
        validated_data['author'] = request.user
        project = Project.objects.create(**validated_data)
        Contributor.objects.create(user=request.user, project=project)
        return project


class IssueSerializer(serializers.ModelSerializer):
    """Serializer pour les issues"""
    author_username = serializers.CharField(source='author.username', read_only=True)
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True, allow_null=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = Issue
        fields = ['id', 'name', 'description', 'priority', 'tag', 'status', 
                  'project', 'project_name', 'author', 'author_username', 
                  'assigned_to', 'assigned_to_username', 'created_time']
        read_only_fields = ['id', 'author', 'created_time']

    def validate_assigned_to(self, value):
        # Vérifier que l'utilisateur assigné est contributeur du projet
        if value:
            project = self.initial_data.get('project') or self.instance.project.id
            if not Contributor.objects.filter(user=value, project_id=project).exists():
                raise serializers.ValidationError(
                    "L'utilisateur assigné doit être contributeur du projet."
                )
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['author'] = request.user
        return Issue.objects.create(**validated_data)


class CommentSerializer(serializers.ModelSerializer):
    """Serializer pour les commentaires"""
    author_username = serializers.CharField(source='author.username', read_only=True)
    issue_name = serializers.CharField(source='issue.name', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'uuid', 'description', 'issue', 'issue_name', 
                  'author', 'author_username', 'created_time']
        read_only_fields = ['id', 'uuid', 'author', 'created_time']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['author'] = request.user
        return Comment.objects.create(**validated_data)