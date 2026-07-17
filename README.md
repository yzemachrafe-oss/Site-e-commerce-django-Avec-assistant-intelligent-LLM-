# 🛍️ Site E-commerce Django

Projet Django complet avec :
- **Côté client** : catalogue de produits, recherche, filtre par catégorie, panier (session), page de commande (checkout).
- **Côté admin (CRUD personnalisé)** : gestion des produits, catégories et commandes via des pages dédiées (`/admin-panel/`).
- **Admin Django natif** aussi disponible sur `/django-admin/`.

## 📦 Installation

```bash
# 1. Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate      # Sur Windows : venv\Scripts\activate

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Appliquer les migrations
python manage.py makemigrations
python manage.py migrate

# 4. Créer un compte administrateur (superutilisateur)
python manage.py createsuperuser

# 5. (Optionnel) Générer des catégories et produits de démonstration
python manage.py donnees_demo

# 6. Lancer le serveur
python manage.py runserver
```

Le site sera accessible sur : http://127.0.0.1:8000/

## 🔗 Pages principales

| Page                         | URL                          |
|------------------------------|-------------------------------|
| Accueil / catalogue           | `/`                            |
| Détail produit                 | `/produit/<slug>/`            |
| Panier                        | `/panier/`                     |
| Passer commande                | `/commande/`                   |
| Connexion admin                | `/connexion/`                  |
| Tableau de bord admin          | `/admin-panel/`                |
| Gestion produits (CRUD)        | `/admin-panel/produits/`       |
| Gestion catégories (CRUD)      | `/admin-panel/categories/`     |
| Gestion commandes              | `/admin-panel/commandes/`      |
| Admin Django natif             | `/django-admin/`               |

## 🗂️ Structure du projet

```
ecommerce/
├── manage.py
├── requirements.txt
├── ecommerce/          # Configuration du projet (settings, urls)
└── shop/               # Application principale
    ├── models.py       # Categorie, Produit, Commande, LigneCommande
    ├── views.py         # Vues client + vues admin CRUD
    ├── forms.py          # Formulaires (Produit, Categorie, Commande)
    ├── urls.py
    ├── admin.py          # Admin Django natif
    ├── templates/shop/
    └── static/shop/
```

## ⚙️ Notes importantes

- Seuls les utilisateurs avec `is_staff=True` peuvent accéder à `/admin-panel/`.
  Le superutilisateur créé avec `createsuperuser` a automatiquement ce statut.
- Le panier est stocké dans la **session** du visiteur (pas besoin de compte client pour commander).
- Lorsqu'une commande est validée, le **stock des produits est automatiquement décrémenté**.
- Pensez à activer `Pillow` pour la gestion des images de produits (déjà inclus dans `requirements.txt`).
- En production : changez `SECRET_KEY`, mettez `DEBUG = False`, configurez `ALLOWED_HOSTS` et une vraie base de données (PostgreSQL par exemple).
