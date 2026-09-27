from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
import re
from io import BytesIO
import sys
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile


def compresser_image(champ_image, largeur_max=1200, qualite=80):
    """
    Compresse et convertit en JPEG une image liée à un ImageField,
    si un nouveau fichier vient d'être uploadé (hasattr(champ_image, 'file')
    est vérifié par l'appelant). Retourne le fichier prêt à assigner
    au champ, ou None si rien à faire.
    """
    if not champ_image or not hasattr(champ_image, 'file'):
        return None

    try:
        img = Image.open(champ_image)
    except Exception:
        return None

    if img.mode != 'RGB':
        img = img.convert('RGB')

    if img.width > largeur_max:
        ratio = largeur_max / img.width
        nouvelle_hauteur = int(img.height * ratio)
        img = img.resize((largeur_max, nouvelle_hauteur), Image.LANCZOS)

    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=qualite, optimize=True)
    buffer.seek(0)

    nom_fichier = champ_image.name.rsplit('.', 1)[0] + '.jpg'

    return InMemoryUploadedFile(
        buffer, 'ImageField', nom_fichier, 'image/jpeg',
        sys.getsizeof(buffer), None
    )


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
        if self.image and hasattr(self.image, 'file'):
            nouveau = compresser_image(self.image, largeur_max=1200)
            if nouveau:
                self.image = nouveau
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
        if self.pk:
            gallery_image = next(iter(self.images.all()), None)
            if gallery_image:
                return gallery_image.image.url
        return None

    def temps_lecture(self):
        mots = len(re.findall(r"\w+", self.contenu))
        minutes = max(1, round(mots / 200))
        return minutes

    def Commentss_approuves(self):
        return self.Commentss.filter(approuve=True)


class ArticleImage(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="articles/%Y/%m/gallery/")
    alt_text = models.CharField(
        max_length=250, blank=True, verbose_name="Texte alternatif"
    )
    position = models.PositiveSmallIntegerField(default=0, verbose_name="Position")

    class Meta:
        ordering = ["position", "id"]
        verbose_name = "Image d’article"
        verbose_name_plural = "Images d’article"

    def __str__(self):
        return self.alt_text or self.image.name.rsplit("/", 1)[-1]

    def save(self, *args, **kwargs):
        if self.image and hasattr(self.image, 'file'):
            nouveau = compresser_image(self.image, largeur_max=1600)
            if nouveau:
                self.image = nouveau
        super().save(*args, **kwargs)


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