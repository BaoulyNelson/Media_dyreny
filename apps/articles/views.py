from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib import messages
from django.db.models import Q
from django.conf import settings
from .models import Article, Categorie, Tag
from .forms import CommentsForm, RechercheForm
from django.views.generic import CreateView, UpdateView, DeleteView, ListView as LV2
from django.urls import reverse_lazy
from .forms import ArticleForm
from .mixins import JournalisteRequiredMixin

class AccueilView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        articles_publies = Article.objects.filter(statut="publie").select_related(
            "auteur", "categorie"
        )
        ctx["article_une"] = articles_publies.filter(en_une=True).first()
        ctx["articles_une"] = articles_publies.filter(en_une=True)[1:4]
        ctx["derniers_articles"] = articles_publies.exclude(en_une=True)[:6]
        ctx["categories"] = Categorie.objects.all()
        ctx["articles_populaires"] = articles_publies.order_by("-vues")[:5]
        return ctx


class ArticleListView(ListView):
    model = Article
    template_name = "articles/liste.html"
    context_object_name = "articles"
    paginate_by = getattr(settings, "ARTICLES_PER_PAGE", 9)

    def get_queryset(self):
        return (
            Article.objects.filter(statut="publie")
            .select_related("auteur", "categorie")
            .order_by("-date_publication")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titre_page"] = "Tous les articles"
        return ctx


class ArticleDetailView(DetailView):
    model = Article
    template_name = "articles/detail.html"
    context_object_name = "article"

    def get_queryset(self):
        return Article.objects.filter(statut="publie").select_related(
            "auteur", "categorie"
        )

    def get_object(self):
        obj = super().get_object()
        obj.incrementer_vues()
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        article = self.object
        ctx["Commentss"] = article.Commentss_approuves()
        ctx["form_Comments"] = CommentsForm()
        ctx["articles_similaires"] = (
            Article.objects.filter(statut="publie", categorie=article.categorie)
            .exclude(pk=article.pk)
            .order_by("-date_publication")[:3]
        )
        return ctx



    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Vous devez être connecté pour commenter.")
            return redirect("accounts:connexion")

        self.object = self.get_object()   # ← self.object au lieu de article = ...
        article = self.object             # alias pratique

        form = CommentsForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.auteur = request.user
            comment.save()
            messages.success(request, "Votre commentaire a été publié avec succès.")
            return redirect(article.get_absolute_url())

        ctx = self.get_context_data()     # ✅ self.object existe maintenant
        ctx["form_Comments"] = form
        return render(request, self.template_name, ctx)





class ArticleParCategorieView(ListView):
    model = Article
    template_name = "articles/liste.html"
    context_object_name = "articles"
    paginate_by = getattr(settings, "ARTICLES_PER_PAGE", 9)

    def get_queryset(self):
        self.categorie = get_object_or_404(Categorie, slug=self.kwargs["slug"])
        return Article.objects.filter(
            statut="publie", categorie=self.categorie
        ).select_related("auteur", "categorie")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categorie"] = self.categorie
        ctx["titre_page"] = f"Catégorie : {self.categorie.nom}"
        return ctx


class ArticleParTagView(ListView):
    model = Article
    template_name = "articles/liste.html"
    context_object_name = "articles"
    paginate_by = getattr(settings, "ARTICLES_PER_PAGE", 9)

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs["slug"])
        return Article.objects.filter(statut="publie", tags=self.tag).select_related(
            "auteur", "categorie"
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tag"] = self.tag
        ctx["titre_page"] = f"Tag : {self.tag.nom}"
        return ctx


class RechercheView(ListView):
    model = Article
    template_name = "articles/recherche.html"
    context_object_name = "articles"
    paginate_by = getattr(settings, "ARTICLES_PER_PAGE", 9)

    def get_queryset(self):
        self.query = self.request.GET.get("q", "").strip()
        if self.query:
            return (
                Article.objects.filter(statut="publie")
                .filter(
                    Q(titre__icontains=self.query)
                    | Q(resume__icontains=self.query)
                    | Q(contenu__icontains=self.query)
                )
                .select_related("auteur", "categorie")
                .distinct()
            )
        return Article.objects.none()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["query"] = self.query
        ctx["form"] = RechercheForm(initial={"q": self.query})
        ctx["titre_page"] = (
            f'Résultats pour "{self.query}"' if self.query else "Recherche"
        )
        return ctx


def error_404(request, exception):
    return render(request, "errors/404.html", status=404)


def error_500(request):
    return render(request, "errors/500.html", status=500)


# ─── PUBLICATION D'ARTICLES (journalistes accrédités uniquement) ─────────────
class MesArticlesView(JournalisteRequiredMixin, LV2):
    model = Article
    template_name = 'articles/mes_articles.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        return Article.objects.filter(auteur=self.request.user).order_by('-date_creation')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titre_page'] = 'Mes articles'
        ctx['stats'] = {
            'total': Article.objects.filter(auteur=self.request.user).count(),
            'publies': Article.objects.filter(auteur=self.request.user, statut='publie').count(),
            'brouillons': Article.objects.filter(auteur=self.request.user, statut='brouillon').count(),
        }
        return ctx


class CreerArticleView(JournalisteRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'articles/form_article.html'

    def form_valid(self, form):
        form.instance.auteur = self.request.user
        messages.success(self.request, "Article créé avec succès !")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('articles:mes_articles')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titre_page'] = 'Nouvel article'
        ctx['action'] = 'Créer'
        return ctx


class ModifierArticleView(JournalisteRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'articles/form_article.html'

    def get_queryset(self):
        # Un journaliste ne peut modifier que ses propres articles
        if self.request.user.is_staff:
            return Article.objects.all()
        return Article.objects.filter(auteur=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Article mis à jour avec succès !")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('articles:mes_articles')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titre_page'] = f"Modifier : {self.object.titre}"
        ctx['action'] = 'Modifier'
        return ctx


class SupprimerArticleView(JournalisteRequiredMixin, DeleteView):
    model = Article
    template_name = 'articles/confirmer_suppression.html'
    success_url = reverse_lazy('articles:mes_articles')

    def get_queryset(self):
        if self.request.user.is_staff:
            return Article.objects.all()
        return Article.objects.filter(auteur=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Article supprimé.")
        return super().form_valid(form)


