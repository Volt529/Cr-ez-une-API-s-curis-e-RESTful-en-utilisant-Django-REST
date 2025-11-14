SoftDesk Support API
API RESTful sécurisée pour le suivi des problèmes techniques, développée avec Django REST Framework.

📋 Description
SoftDesk Support est une API permettant aux entreprises de gérer des projets collaboratifs avec un système de suivi des problèmes (issues) et de commentaires. L'application est conçue pour servir des applications front-end sur différentes plateformes (Web, iOS, Android).
Fonctionnalités principales

Authentification JWT sécurisée : Tokens d'accès courte durée (5 minutes)
Gestion des utilisateurs : Inscription avec validation RGPD (âge minimum 15 ans)
Projets multi-contributeurs : Création et gestion collaborative
Suivi des problèmes : Issues avec priorités, tags et statuts
Système de commentaires : Communication entre contributeurs
Permissions granulaires : Contrôle d'accès basé sur les rôles (OWASP)
Pagination : Optimisation des performances (Green Code)

🛠️ Technologies

Python 3.11+
Django 5.0.1
Django REST Framework 3.14.0
djangorestframework-simplejwt 5.3.1
drf-nested-routers 0.93.5
SQLite3 (développement) / PostgreSQL (production)

📦 Installation
Prérequis

Python 3.11 ou supérieur
pip (gestionnaire de paquets Python)
Git

Étapes d'installation
1. Cloner le repository
bashgit clone https://github.com/VOTRE_USERNAME/softdesk-api.git
cd softdesk-api
2. Créer un environnement virtuel
Windows :
bashpython -m venv env
env\Scripts\activate
macOS/Linux :
bashpython3 -m venv env
source env/bin/activate
3. Installer les dépendances
bashpip install -r requirements.txt
4. Configurer la base de données
bashpython manage.py makemigrations
python manage.py migrate
5. (Optionnel) Créer un superutilisateur
bashpython manage.py createsuperuser
Suivez les instructions pour créer un compte administrateur.

6. Lancer le serveur de développement
bashpython manage.py runserver
L'API sera accessible sur http://127.0.0.1:8000/api/
L'interface d'administration : http://127.0.0.1:8000/admin/

🚀 Utilisation
Authentification
Créer un compte
bashPOST /api/users/
Content-Type: application/json

{
  "username": "alice",
  "email": "alice@example.com",
  "password": "SecurePass123!",
  "password2": "SecurePass123!",
  "age": 28,
  "can_be_contacted": true,
  "can_data_be_shared": false
}
Se connecter (obtenir un token JWT)
bashPOST /api/login/
Content-Type: application/json

{
  "username": "alice",
  "password": "SecurePass123!"
}
Réponse :
json{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
Utiliser le token
Pour toutes les requêtes authentifiées, ajoutez le header :
Authorization: Bearer {votre_access_token}

Exemples d'utilisation
Créer un projet
bashPOST /api/projects/
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Application Mobile Banking",
  "description": "Application de gestion bancaire",
  "type": "iOS"
}
Types de projets disponibles : back-end, front-end, iOS, Android
Créer une issue
bashPOST /api/projects/1/issues/
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Bug d'affichage",
  "description": "Le solde ne s'affiche pas correctement",
  "priority": "HIGH",
  "tag": "BUG",
  "status": "To Do",
  "project": 1
}
Options :

Priorité : LOW, MEDIUM, HIGH
Tag : BUG, FEATURE, TASK
Statut : To Do, In Progress, Finished

Créer un commentaire
bashPOST /api/projects/1/issues/1/comments/
Authorization: Bearer {token}
Content-Type: application/json

{
  "description": "J'ai identifié la source du problème",
  "issue": 1
}
🧪 Tests
Lancer les tests automatisés
Un script de test complet valide toutes les fonctionnalités :
bashpython test_api.py
Ce script teste :

✅ Création d'utilisateurs
✅ Authentification JWT
✅ Validation RGPD (rejet des mineurs < 15 ans)
✅ Création de projets
✅ Gestion des contributeurs
✅ Permissions OWASP (403 Forbidden)
✅ Création d'issues et commentaires
✅ Pagination (Green Code)

Réinitialiser la base de données de test
bashpython reset_db.py
🔐 Sécurité (OWASP)
L'API respecte les recommandations OWASP Top 10 :
Authentification

JWT avec tokens à expiration courte (5 minutes)
Refresh tokens valides 1 jour
Rotation automatique des tokens

Autorisation

Seuls les contributeurs d'un projet peuvent y accéder
Utilisateur authentifié obligatoire pour toutes les ressources

Permissions granulaires

Lecture : Tous les contributeurs
Modification : Auteur uniquement
Suppression : Auteur uniquement

Exemple : Bob peut voir une issue créée par Alice, mais ne peut ni la modifier ni la supprimer.
🛡️ Conformité RGPD
Vérification de l'âge

Âge minimum : 15 ans
Validation automatique à l'inscription
Rejet avec message d'erreur si âge < 15

Consentement explicite

can_be_contacted : L'utilisateur accepte d'être contacté
can_data_be_shared : L'utilisateur accepte le partage de ses données

Droits des utilisateurs

Droit à l'accès : GET /api/users/{id}/
Droit à la rectification : PUT /api/users/{id}/
Droit à l'oubli : DELETE /api/users/{id}/

🌱 Green Code
Pagination systématique

Toutes les listes sont paginées
10 items par page par défaut (configurable jusqu'à 100)
Évite la surcharge serveur avec de gros volumes de données

Exemple de réponse paginée :
json{
  "count": 156,
  "next": "http://api.../projects/?page=2",
  "previous": null,
  "results": [...]
}
Autres optimisations

Requêtes filtrées côté serveur
Structure modulaire pour faciliter la maintenance
Code optimisé et commenté

}
📖 Documentation supplémentaire

Interface Django REST Framework : http://127.0.0.1:8000/api/ (interface web interactive)
Interface d'administration : http://127.0.0.1:8000/admin/ (nécessite un superutilisateur)
POSTMAN_GUIDE.md : Guide détaillé pour tester avec Postman
