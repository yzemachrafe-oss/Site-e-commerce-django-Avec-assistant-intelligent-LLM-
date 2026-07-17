from django.core.management.base import BaseCommand
from shop.models import Categorie, Produit


class Command(BaseCommand):
    help = "Crée des catégories et produits de démonstration."

    def handle(self, *args, **options):
        categories_data = ['Vêtements', 'Électronique', 'Maison & Cuisine', 'Beauté']
        categories = {}
        for nom in categories_data:
            cat, _ = Categorie.objects.get_or_create(nom=nom)
            categories[nom] = cat

        produits_data = [
            ('T-shirt en coton', 'Vêtements', 129.00, 25, "T-shirt 100% coton, coupe classique."),
            ('Jean slim', 'Vêtements', 349.00, 15, "Jean slim confortable, plusieurs tailles disponibles."),
            ('Casque Bluetooth', 'Électronique', 449.00, 10, "Casque sans fil avec réduction de bruit."),
            ('Chargeur rapide USB-C', 'Électronique', 149.00, 30, "Chargeur rapide 30W compatible avec la plupart des appareils."),
            ('Set de casseroles', 'Maison & Cuisine', 599.00, 8, "Set de 5 casseroles antiadhésives."),
            ('Machine à café', 'Maison & Cuisine', 899.00, 5, "Machine à café automatique avec broyeur intégré."),
            ('Crème hydratante', 'Beauté', 89.00, 40, "Crème hydratante visage pour tous types de peau."),
            ('Parfum homme', 'Beauté', 259.00, 12, "Eau de parfum boisée, tenue longue durée."),
        ]

        for nom, cat_nom, prix, stock, description in produits_data:
            Produit.objects.get_or_create(
                nom=nom,
                defaults={
                    'categorie': categories[cat_nom],
                    'prix': prix,
                    'stock': stock,
                    'description': description,
                    'disponible': True,
                }
            )

        self.stdout.write(self.style.SUCCESS(
            f"✅ {len(categories_data)} catégories et {len(produits_data)} produits créés avec succès."
        ))
