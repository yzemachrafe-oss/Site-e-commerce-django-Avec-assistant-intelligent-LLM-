def panier_context(request):
    """Rend le nombre d'articles du panier disponible dans tous les templates."""
    panier = request.session.get('panier', {})
    nombre_articles = sum(item['quantite'] for item in panier.values())
    return {'panier_nombre_articles': nombre_articles}
