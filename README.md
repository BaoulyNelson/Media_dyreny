# Le Média — Site web Django 4.2

Un média en ligne professionnel construit avec Django 4.2.16, entièrement en français.

## Démarrage rapide

```bash
# 1. Cloner / décompresser le projet
cd media_site

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Appliquer les migrations
python manage.py migrate

# 5. Créer les données de démonstration
python manage.py populate_demo

# 6. Lancer le serveur
python manage.py runserver
```

Accédez à http://127.0.0.1:8000/

## Comptes de démonstration

| Rôle          | Identifiant   | Mot de passe       |
|---------------|---------------|--------------------|
| Administrateur| admin         | admin1234          |
| Journaliste   | journaliste   | journaliste1234    |

Interface d'administration : http://127.0.0.1:8000/admin/

## Fonctionnalités

- Page d'accueil avec articles à la une
- Liste des articles avec pagination
- Pages de détail avec Commentss
- Recherche full-text
- Catégories et tags
- Authentification (inscription, connexion, profil)
- Formulaire de contact
- Interface d'administration complète
- Design responsive Bootstrap 5

## Structure du projet

```
media_site/
├── config/          # Configuration Django
├── articles/        # App principale (articles, Commentss)
├── accounts/        # Authentification et profils
├── contact/         # Formulaire de contact
├── templates/       # Templates HTML
├── static/          # CSS, JS, images
└── manage.py
```
