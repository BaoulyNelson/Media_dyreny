from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages


class JournalisteRequiredMixin(UserPassesTestMixin):
    """
    Autorise uniquement les utilisateurs membres du groupe 'Journalistes'
    ou les administrateurs (is_staff).
    """

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_staff or
            user.groups.filter(name='Journalistes').exists()
        )

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            messages.warning(self.request, "Vous devez être connecté pour accéder à cette page.")
            return redirect('accounts:connexion')
        messages.error(
            self.request,
            "Accès refusé. Seuls les journalistes accrédités peuvent publier des articles. "
            "Contactez l'administration pour obtenir les droits de publication."
        )
        return redirect('articles:accueil')
