from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
import re


class Categorie(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Nom")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Description")
    couleur = models.CharField(
        max_length=7, default="#e63946", verbose_name="Couleur (hex)"
    )

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ["nom"]

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("articles:par_categorie", kwargs={"slug": self.slug})

    def nombre_articles(self):
        return self.articles.filter(statut="publie").count()


class Tag(models.Model):
    nom = models.CharField(max_length=50, verbose_name="Nom")
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)


class Article(models.Model):
    STATUT_CHOICES = [
        ("brouillon", "Brouillon"),
        ("publie", "Publié"),
        ("archive", "Archivé"),
    ]

    titre = models.CharField(max_length=250, verbose_name="Titre")
    slug = models.SlugField(unique=True, max_length=250, verbose_name="Slug")
    auteur = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="articles", verbose_name="Auteur"
    )
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
        verbose_name="Catégorie",
    )
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Tags")
    resume = models.TextField(max_length=500, verbose_name="Résumé")
    contenu = models.TextField(verbose_name="Contenu")
    image = models.ImageField(
        upload_to="articles/%Y/%m/",
        blank=True,
        null=True,
        verbose_name="Image principale",
    )
    image_url = models.URLField(blank=True, verbose_name="URL image externe")
    statut = models.CharField(
        max_length=10,
        choices=STATUT_CHOICES,
        default="brouillon",
        verbose_name="Statut",
    )
    en_une = models.BooleanField(default=False, verbose_name="À la une")
    vues = models.PositiveIntegerField(default=0, verbose_name="Nombre de vues")
    date_creation = models.DateTimeField(
        auto_now_add=True, verbose_name="Date de création"
    )
    date_modification = models.DateTimeField(
        auto_now=True, verbose_name="Dernière modification"
    )
    date_publication = models.DateTimeField(
        null=True, blank=True, verbose_name="Date de publication"
    )

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ["-date_publication", "-date_creation"]

    def __str__(self):
        return self.titre

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.titre)
            slug = base_slug
            n = 1
            while Article.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug
        if self.statut == "publie" and not self.date_publication:
            self.date_publication = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("articles:detail", kwargs={"slug": self.slug})

    def incrementer_vues(self):
        Article.objects.filter(pk=self.pk).update(vues=models.F("vues") + 1)

    def get_image_url(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return None

    def temps_lecture(self):
        mots = len(re.findall(r"\w+", self.contenu))
        minutes = max(1, round(mots / 200))
        return minutes

    def Commentss_approuves(self):
        return self.Commentss.filter(approuve=True)


class Comments(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="Commentss"
    )
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Commentss")
    contenu = models.TextField(max_length=1000, verbose_name="Comments")
    approuve = models.BooleanField(default=True, verbose_name="Approuvé")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Comments"
        verbose_name_plural = "Commentss"
        ordering = ["-date_creation"]

    def __str__(self):
        return f"Comments de {self.auteur.username} sur {self.article.titre[:30]}"
