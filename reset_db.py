"""
Script pour réinitialiser la base de données avant les tests
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from softdesk.models import User, Project, Contributor, Issue, Comment

print("🗑️  Suppression des données de test...")

# Supprimer dans l'ordre inverse des dépendances
Comment.objects.all().delete()
print("   ✅ Commentaires supprimés")

Issue.objects.all().delete()
print("   ✅ Issues supprimées")

Contributor.objects.all().delete()
print("   ✅ Contributeurs supprimés")

Project.objects.all().delete()
print("   ✅ Projets supprimés")

# Supprimer seulement les utilisateurs de test (pas le superuser)
User.objects.filter(is_superuser=False).delete()
print("   ✅ Utilisateurs de test supprimés")

print("\n✨ Base de données réinitialisée avec succès !")
print("Vous pouvez maintenant lancer : python test_api.py")