from django import forms
from .models import Produit, Categorie, Commande


class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la catégorie'}),
        }


class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['nom', 'categorie', 'description', 'prix', 'stock', 'image', 'disponible']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'prix': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ['client_nom', 'client_email', 'client_telephone', 'adresse', 'ville', 'code_postal', 'note']
        widgets = {
            'client_nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom complet'}),
            'client_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'exemple@email.com'}),
            'client_telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '06 12 34 56 78'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adresse de livraison'}),
            'ville': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ville'}),
            'code_postal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Code postal (optionnel)'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Instructions particulières...'}),
        }
