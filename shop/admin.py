from django.contrib import admin
from .models import Categorie, Produit, Commande, LigneCommande


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'slug')
    prepopulated_fields = {'slug': ('nom',)}
    search_fields = ('nom',)


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'categorie', 'prix', 'stock', 'disponible', 'date_creation')
    list_filter = ('categorie', 'disponible')
    search_fields = ('nom', 'description')
    prepopulated_fields = {'slug': ('nom',)}
    list_editable = ('prix', 'stock', 'disponible')


class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 0
    readonly_fields = ('produit', 'nom_produit', 'prix_unitaire', 'quantite')


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_nom', 'client_email', 'ville', 'statut', 'total', 'date_commande')
    list_filter = ('statut', 'date_commande')
    search_fields = ('client_nom', 'client_email', 'client_telephone')
    inlines = [LigneCommandeInline]
    list_editable = ('statut',)
