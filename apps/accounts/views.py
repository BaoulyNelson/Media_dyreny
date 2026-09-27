from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, TemplateView, DetailView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import ConnexionForm, InscriptionForm, ProfilForm
from .models import ProfilUtilisateur
from apps.articles.models import Article, Comments


class ConnexionView(LoginView):
    template_name = "accounts/connexion.html"
    form_class = ConnexionForm
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titre_page"] = "Connexion"
        return ctx

    def form_valid(self, form):
        messages.success(self.request, f"Bienvenue, {form.get_user().username} !")
        return super().form_valid(form)


class DeconnexionView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "Vous avez été déconnecté avec succès.")
        return super().dispatch(request, *args, **kwargs)


class InscriptionView(CreateView):
    form_class = InscriptionForm
    template_name = "accounts/inscription.html"
    success_url = reverse_lazy("articles:accueil")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("articles:accueil")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            "Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter.",
        )
        from django.contrib.auth import login

        login(self.request, self.object)
        return redirect("articles:accueil")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titre_page"] = "Créer un compte"
        return ctx


class ProfilView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profil.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["mes_articles"] = Article.objects.filter(
            auteur=user, statut="publie"
        ).order_by("-date_publication")[:5]
        ctx["mes_Commentss"] = Comments.objects.filter(auteur=user).order_by(
            "-date_creation"
        )[:5]
        ctx["titre_page"] = "Mon profil"
        return ctx


class ModifierProfilView(LoginRequiredMixin, UpdateView):
    model = ProfilUtilisateur
    form_class = ProfilForm
    template_name = "accounts/modifier_profil.html"
    success_url = reverse_lazy("accounts:profil")

    def get_object(self):
        return self.request.user.profil

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        user.first_name = form.cleaned_data["first_name"]
        user.last_name = form.cleaned_data["last_name"]
        user.email = form.cleaned_data["email"]
        user.save()
        messages.success(self.request, "Votre profil a été mis à jour avec succès.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titre_page"] = "Modifier mon profil"
        return ctx
