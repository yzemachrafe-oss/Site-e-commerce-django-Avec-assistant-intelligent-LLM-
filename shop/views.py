import os
from decimal import Decimal
from groq import Groq
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
import json
from django.views.decorators.csrf import csrf_exempt
from .models import Categorie, Produit, Commande, LigneCommande
from .forms import ProduitForm, CategorieForm, CommandeForm

est_staff = user_passes_test(lambda u: u.is_staff, login_url='shop:connexion')


# =====================================================================
#  CÔTÉ CLIENT
# =====================================================================

def accueil(request):
    produits = Produit.objects.filter(disponible=True)
    categories = Categorie.objects.all()

    categorie_slug = request.GET.get('categorie')
    if categorie_slug:
        produits = produits.filter(categorie__slug=categorie_slug)

    recherche = request.GET.get('q')
    if recherche:
        produits = produits.filter(
            Q(nom__icontains=recherche) | Q(description__icontains=recherche)
        )

    return render(request, 'shop/accueil.html', {
        'produits': produits,
        'categories': categories,
        'categorie_active': categorie_slug,
        'recherche': recherche or '',
    })


def produit_detail(request, slug):
    produit = get_object_or_404(Produit, slug=slug, disponible=True)
    produits_similaires = Produit.objects.filter(
        categorie=produit.categorie, disponible=True
    ).exclude(pk=produit.pk)[:4]
    return render(request, 'shop/produit_detail.html', {
        'produit': produit,
        'produits_similaires': produits_similaires,
    })


def _get_panier(request):
    return request.session.get('panier', {})


def _save_panier(request, panier):
    request.session['panier'] = panier
    request.session.modified = True


def panier_ajouter(request, produit_id):
    produit = get_object_or_404(Produit, pk=produit_id, disponible=True)
    panier = _get_panier(request)
    key = str(produit_id)

    quantite = int(request.POST.get('quantite', 1)) if request.method == 'POST' else 1

    if key in panier:
        panier[key]['quantite'] += quantite
    else:
        panier[key] = {'quantite': quantite}

    # on ne dépasse pas le stock disponible
    if panier[key]['quantite'] > produit.stock:
        panier[key]['quantite'] = produit.stock
        messages.warning(request, f"Stock limité : seulement {produit.stock} unité(s) de « {produit.nom} » disponible(s).")
    else:
        messages.success(request, f"« {produit.nom} » a été ajouté au panier.")

    _save_panier(request, panier)
    return redirect(request.POST.get('next') or 'shop:accueil')


def panier_maj(request, produit_id):
    if request.method == 'POST':
        panier = _get_panier(request)
        key = str(produit_id)
        try:
            quantite = int(request.POST.get('quantite', 1))
        except ValueError:
            quantite = 1

        produit = get_object_or_404(Produit, pk=produit_id)
        if key in panier:
            if quantite <= 0:
                del panier[key]
            else:
                panier[key]['quantite'] = min(quantite, produit.stock)
            _save_panier(request, panier)
    return redirect('shop:panier')


def panier_supprimer(request, produit_id):
    panier = _get_panier(request)
    key = str(produit_id)
    if key in panier:
        del panier[key]
        _save_panier(request, panier)
        messages.info(request, "Produit retiré du panier.")
    return redirect('shop:panier')


def _panier_details(request):
    """Retourne la liste des lignes du panier + le total, à partir de la session."""
    panier = _get_panier(request)
    lignes = []
    total = Decimal('0')
    produits_ids = [int(pid) for pid in panier.keys()]
    produits = Produit.objects.filter(pk__in=produits_ids)
    produits_map = {p.pk: p for p in produits}

    for pid_str, data in panier.items():
        produit = produits_map.get(int(pid_str))
        if not produit:
            continue
        quantite = data['quantite']
        sous_total = produit.prix * quantite
        total += sous_total
        lignes.append({
            'produit': produit,
            'quantite': quantite,
            'sous_total': sous_total,
        })
    return lignes, total


def panier_voir(request):
    lignes, total = _panier_details(request)
    return render(request, 'shop/panier.html', {'lignes': lignes, 'total': total})


def commande_creer(request):
    lignes, total = _panier_details(request)
    if not lignes:
        messages.warning(request, "Votre panier est vide.")
        return redirect('shop:accueil')

    if request.method == 'POST':
        form = CommandeForm(request.POST)
        if form.is_valid():
            commande = form.save()
            for ligne in lignes:
                LigneCommande.objects.create(
                    commande=commande,
                    produit=ligne['produit'],
                    nom_produit=ligne['produit'].nom,
                    prix_unitaire=ligne['produit'].prix,
                    quantite=ligne['quantite'],
                )
                # on décrémente le stock
                produit = ligne['produit']
                produit.stock = max(0, produit.stock - ligne['quantite'])
                produit.save()

            # panier vidé après la commande
            request.session['panier'] = {}
            request.session.modified = True

            messages.success(request, "Votre commande a bien été enregistrée !")
            return redirect('shop:commande_succes', commande_id=commande.pk)
    else:
        form = CommandeForm()

    return render(request, 'shop/commande.html', {
        'form': form, 'lignes': lignes, 'total': total,
    })


def commande_succes(request, commande_id):
    commande = get_object_or_404(Commande, pk=commande_id)
    return render(request, 'shop/commande_succes.html', {'commande': commande})


# =====================================================================
#  ESPACE ADMIN PERSONNALISÉ (CRUD) — réservé au staff
# =====================================================================

@login_required
@est_staff
def admin_dashboard(request):
    contexte = {
        'nb_produits': Produit.objects.count(),
        'nb_categories': Categorie.objects.count(),
        'nb_commandes': Commande.objects.count(),
        'nb_commandes_attente': Commande.objects.filter(statut='en_attente').count(),
        'dernieres_commandes': Commande.objects.all()[:5],
    }
    return render(request, 'shop/admin/dashboard.html', contexte)


# ---- CRUD Produits ----

@login_required
@est_staff
def admin_produit_liste(request):
    produits = Produit.objects.all()
    return render(request, 'shop/admin/produit_liste.html', {'produits': produits})


@login_required
@est_staff
def admin_produit_ajouter(request):
    if request.method == 'POST':
        form = ProduitForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Produit ajouté avec succès.")
            return redirect('shop:admin_produit_liste')
    else:
        form = ProduitForm()
    return render(request, 'shop/admin/produit_form.html', {'form': form, 'titre': 'Ajouter un produit'})


@login_required
@est_staff
def admin_produit_modifier(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        form = ProduitForm(request.POST, request.FILES, instance=produit)
        if form.is_valid():
            form.save()
            messages.success(request, "Produit modifié avec succès.")
            return redirect('shop:admin_produit_liste')
    else:
        form = ProduitForm(instance=produit)
    return render(request, 'shop/admin/produit_form.html', {
        'form': form, 'titre': f'Modifier « {produit.nom} »', 'produit': produit,
    })


@login_required
@est_staff
def admin_produit_supprimer(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        produit.delete()
        messages.success(request, "Produit supprimé.")
        return redirect('shop:admin_produit_liste')
    return render(request, 'shop/admin/produit_confirm_delete.html', {'produit': produit})


# ---- CRUD Catégories ----

@login_required
@est_staff
def admin_categorie_liste(request):
    categories = Categorie.objects.all()
    return render(request, 'shop/admin/categorie_liste.html', {'categories': categories})


@login_required
@est_staff
def admin_categorie_ajouter(request):
    if request.method == 'POST':
        form = CategorieForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Catégorie ajoutée avec succès.")
            return redirect('shop:admin_categorie_liste')
    else:
        form = CategorieForm()
    return render(request, 'shop/admin/categorie_form.html', {'form': form, 'titre': 'Ajouter une catégorie'})


@login_required
@est_staff
def admin_categorie_modifier(request, pk):
    categorie = get_object_or_404(Categorie, pk=pk)
    if request.method == 'POST':
        form = CategorieForm(request.POST, instance=categorie)
        if form.is_valid():
            form.save()
            messages.success(request, "Catégorie modifiée avec succès.")
            return redirect('shop:admin_categorie_liste')
    else:
        form = CategorieForm(instance=categorie)
    return render(request, 'shop/admin/categorie_form.html', {
        'form': form, 'titre': f'Modifier « {categorie.nom} »',
    })


@login_required
@est_staff
def admin_categorie_supprimer(request, pk):
    categorie = get_object_or_404(Categorie, pk=pk)
    if request.method == 'POST':
        categorie.delete()
        messages.success(request, "Catégorie supprimée.")
        return redirect('shop:admin_categorie_liste')
    return render(request, 'shop/admin/categorie_confirm_delete.html', {'categorie': categorie})


# ---- Commandes (lecture + changement de statut) ----

@login_required
@est_staff
def admin_commande_liste(request):
    commandes = Commande.objects.all()
    statut = request.GET.get('statut')
    if statut:
        commandes = commandes.filter(statut=statut)
    return render(request, 'shop/admin/commande_liste.html', {
        'commandes': commandes, 'statut_filtre': statut or '',
    })


@login_required
@est_staff
def admin_commande_detail(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    if request.method == 'POST':
        nouveau_statut = request.POST.get('statut')
        if nouveau_statut:
            commande.statut = nouveau_statut
            commande.save()
            messages.success(request, "Statut de la commande mis à jour.")
            return redirect('shop:admin_commande_detail', pk=pk)
    return render(request, 'shop/admin/commande_detail.html', {'commande': commande})


# =====================================================================
#  ASSISTANT INTELLIGENT (Groq)
# =====================================================================

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


@csrf_exempt
def chatbot_view(request):
    if request.method == "POST":
        try:
            user_message = ""

            # قراءة الميساج كيفما صيفطو الـ JavaScript
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                user_message = data.get('message', '')
            else:
                user_message = request.POST.get('message', '')

            if not user_message:
                return JsonResponse({'status': 'error', 'reply': 'الميساج خاوي!'})

            # إرسال الطلب لـ Groq
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "أنت مساعد ذكي لمتجر إلكتروني. جاوب دائما بنفس اللغة اللي كتب بيها العميل سؤاله: إلا كتب بالدارجة المغربية جاوب بالدارجة، إلا كتب بالفرنسية جاوب بالفرنسية، إلا كتب بالإنجليزية جاوب بالإنجليزية."
                    },
                    {"role": "user", "content": user_message}
                ],
            )

            return JsonResponse({'status': 'success', 'reply': response.choices[0].message.content})

        except Exception as e:
            print("🚨 الـ Error الحقيقي هو:")
            print(e)
            return JsonResponse({'status': 'error', 'reply': 'السموحة منك، وقع مشكل ف السيستيم. حاول شوية آخر.'})

    return render(request, 'shop/chatbot.html')
