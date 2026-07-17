from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'shop'

urlpatterns = [
    # ---------- Côté client ----------
    path('', views.accueil, name='accueil'),
    path('produit/<slug:slug>/', views.produit_detail, name='produit_detail'),

    path('panier/', views.panier_voir, name='panier'),
    path('panier/ajouter/<int:produit_id>/', views.panier_ajouter, name='panier_ajouter'),
    path('panier/maj/<int:produit_id>/', views.panier_maj, name='panier_maj'),
    path('panier/supprimer/<int:produit_id>/', views.panier_supprimer, name='panier_supprimer'),

    path('commande/', views.commande_creer, name='commande'),
    path('commande/succes/<int:commande_id>/', views.commande_succes, name='commande_succes'),

    # ---------- Authentification (pour l'espace admin) ----------
    path('connexion/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='connexion'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='deconnexion'),

    # ---------- Espace admin personnalisé (CRUD) ----------
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),

    path('admin-panel/produits/', views.admin_produit_liste, name='admin_produit_liste'),
    path('admin-panel/produits/ajouter/', views.admin_produit_ajouter, name='admin_produit_ajouter'),
    path('admin-panel/produits/<int:pk>/modifier/', views.admin_produit_modifier, name='admin_produit_modifier'),
    path('admin-panel/produits/<int:pk>/supprimer/', views.admin_produit_supprimer, name='admin_produit_supprimer'),

    path('admin-panel/categories/', views.admin_categorie_liste, name='admin_categorie_liste'),
    path('admin-panel/categories/ajouter/', views.admin_categorie_ajouter, name='admin_categorie_ajouter'),
    path('admin-panel/categories/<int:pk>/modifier/', views.admin_categorie_modifier, name='admin_categorie_modifier'),
    path('admin-panel/categories/<int:pk>/supprimer/', views.admin_categorie_supprimer, name='admin_categorie_supprimer'),

    path('admin-panel/commandes/', views.admin_commande_liste, name='admin_commande_liste'),
    path('admin-panel/commandes/<int:pk>/', views.admin_commande_detail, name='admin_commande_detail'),
    path('assistant/', views.chatbot_view, name='assistant'),
]
