from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['nom']

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)


class Produit(models.Model):
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True,
                                   blank=True, related_name='produits')
    nom = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='produits/', blank=True, null=True)
    disponible = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_maj = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['-date_creation']

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nom)
            slug = base_slug
            i = 1
            while Produit.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base_slug}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:produit_detail', args=[self.slug])

    @property
    def en_stock(self):
        return self.stock > 0


STATUT_CHOICES = [
    ('en_attente', 'En attente'),
    ('confirmee', 'Confirmée'),
    ('expediee', 'Expédiée'),
    ('livree', 'Livrée'),
    ('annulee', 'Annulée'),
]


class Commande(models.Model):
    STATUT_CHOICES = STATUT_CHOICES  # accessible depuis les templates : commande.STATUT_CHOICES

    client_nom = models.CharField("Nom complet", max_length=150)
    client_email = models.EmailField("Email")
    client_telephone = models.CharField("Téléphone", max_length=30)
    adresse = models.CharField("Adresse", max_length=255)
    ville = models.CharField("Ville", max_length=100)
    code_postal = models.CharField("Code postal", max_length=20, blank=True)
    note = models.TextField("Note (optionnel)", blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_commande = models.DateTimeField(auto_now_add=True)
    date_maj = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-date_commande']

    def __str__(self):
        return f"Commande #{self.pk} - {self.client_nom}"

    @property
    def total(self):
        return sum(ligne.sous_total for ligne in self.lignes.all())

    @property
    def nombre_articles(self):
        return sum(ligne.quantite for ligne in self.lignes.all())


class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.SET_NULL, null=True)
    nom_produit = models.CharField(max_length=200)  # copie au cas où le produit est supprimé
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    quantite = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Ligne de commande"
        verbose_name_plural = "Lignes de commande"

    def __str__(self):
        return f"{self.quantite} x {self.nom_produit}"

    @property
    def sous_total(self):
        return self.prix_unitaire * self.quantite
