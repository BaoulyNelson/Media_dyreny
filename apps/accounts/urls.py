from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .forms import StyledPasswordResetForm, StyledSetPasswordForm
from . import views

app_name = "accounts"

urlpatterns = [
    path("connexion/", views.ConnexionView.as_view(), name="connexion"),
    path("deconnexion/", views.DeconnexionView.as_view(), name="deconnexion"),
    path("inscription/", views.InscriptionView.as_view(), name="inscription"),
    path("profil/", views.ProfilView.as_view(), name="profil"),
    path(
        "profil/modifier/", views.ModifierProfilView.as_view(), name="modifier_profil"
    ),
    path(
        "mot-de-passe-oublie/",
        auth_views.PasswordResetView.as_view(
            form_class=StyledPasswordResetForm,
            template_name="accounts/password_reset_form.html",
            email_template_name="accounts/password_reset_email.html",
            success_url=reverse_lazy("accounts:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "mot-de-passe-oublie/envoye/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reinitialiser/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            form_class=StyledSetPasswordForm,
            template_name="accounts/password_reset_confirm.html",
            success_url=reverse_lazy("accounts:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reinitialiser/termine/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
