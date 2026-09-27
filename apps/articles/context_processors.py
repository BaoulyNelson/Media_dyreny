from .models import Categorie


def categories_processor(request):
    return {
        'nav_categories': Categorie.objects.all()[:6]
    }


def journalist_processor(request):
    """Expose si l'utilisateur est journaliste ou admin dans tous les templates."""
    is_journalist = False
    if request.user.is_authenticated:
        is_journalist = (
            request.user.is_staff or
            request.user.groups.filter(name='Journalistes').exists()
        )
    # ✅ CORRECTION : retourner la variable pour qu'elle soit accessible dans les templates
    return {'est_journaliste': is_journalist}