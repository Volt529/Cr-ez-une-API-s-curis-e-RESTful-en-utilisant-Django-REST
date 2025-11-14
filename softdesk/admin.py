from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Project, Contributor, Issue, Comment


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Administration personnalisée pour le modèle User"""
    list_display = ['username', 'email', 'age', 'can_be_contacted', 'can_data_be_shared', 'date_joined']
    list_filter = ['can_be_contacted', 'can_data_be_shared', 'is_staff']
    search_fields = ['username', 'email']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations RGPD', {
            'fields': ('age', 'can_be_contacted', 'can_data_be_shared')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informations RGPD', {
            'fields': ('age', 'can_be_contacted', 'can_data_be_shared')
        }),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Administration pour les projets"""
    list_display = ['name', 'type', 'author', 'created_time']
    list_filter = ['type', 'created_time']
    search_fields = ['name', 'description']
    readonly_fields = ['created_time']
    
    fieldsets = (
        ('Informations du projet', {
            'fields': ('name', 'description', 'type')
        }),
        ('Métadonnées', {
            'fields': ('author', 'created_time')
        }),
    )


@admin.register(Contributor)
class ContributorAdmin(admin.ModelAdmin):
    """Administration pour les contributeurs"""
    list_display = ['user', 'project', 'created_time']
    list_filter = ['created_time']
    search_fields = ['user__username', 'project__name']
    readonly_fields = ['created_time']


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    """Administration pour les issues"""
    list_display = ['name', 'project', 'priority', 'tag', 'status', 'author', 'assigned_to', 'created_time']
    list_filter = ['priority', 'tag', 'status', 'created_time']
    search_fields = ['name', 'description', 'project__name']
    readonly_fields = ['created_time']
    
    fieldsets = (
        ('Informations de l\'issue', {
            'fields': ('name', 'description', 'project')
        }),
        ('Classification', {
            'fields': ('priority', 'tag', 'status')
        }),
        ('Attribution', {
            'fields': ('author', 'assigned_to')
        }),
        ('Métadonnées', {
            'fields': ('created_time',)
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Administration pour les commentaires"""
    list_display = ['uuid', 'issue', 'author', 'created_time']
    list_filter = ['created_time']
    search_fields = ['description', 'issue__name', 'author__username']
    readonly_fields = ['uuid', 'created_time']
    
    fieldsets = (
        ('Commentaire', {
            'fields': ('uuid', 'description', 'issue')
        }),
        ('Métadonnées', {
            'fields': ('author', 'created_time')
        }),
    )