from io import BytesIO
import tempfile

from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .forms import ArticleForm
from .models import Article, ArticleImage, Categorie


class ArticleGalleryTests(TestCase):
    def setUp(self):
        self.media_directory = tempfile.TemporaryDirectory()
        self.settings_override = override_settings(
            MEDIA_ROOT=self.media_directory.name,
            SITE_URL="https://journal.example",
            ALLOWED_HOSTS=["testserver"],
        )
        self.settings_override.enable()
        self.user = User.objects.create_user(username="reporter", password="pass")

    def tearDown(self):
        self.settings_override.disable()
        self.media_directory.cleanup()

    def make_image(self, name, color):
        image = Image.new("RGB", (4, 4), color=color)
        content = BytesIO()
        image.save(content, format="PNG")
        return SimpleUploadedFile(name, content.getvalue(), content_type="image/png")

    def test_article_form_generates_summary_and_sanitizes_rich_content(self):
        form = ArticleForm(
            data={
                "titre": "Un titre suffisamment long",
                "resume": "",
                "contenu": "<p>Un contenu assez long pour créer automatiquement un résumé utile.</p><script>alert('x')</script>",
                "image_url": "",
                "statut": "brouillon",
                "images_to_delete": [],
            },
            instance=Article(auteur=self.user),
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(
            form.cleaned_data["resume"],
            "Un contenu assez long pour créer automatiquement un résumé utile.",
        )
        self.assertNotIn("<script>", form.cleaned_data["contenu"])

    def test_article_form_uses_rich_editor_and_styled_fields(self):
        form = ArticleForm()

        self.assertEqual(
            form.fields["contenu"].widget.__class__.__name__, "CKEditor5Widget"
        )
        self.assertEqual(
            form.fields["titre"].widget.attrs["class"], "form-control form-control-lg"
        )
        self.assertEqual(form.fields["resume"].widget.attrs["class"], "form-control")

    def test_uploads_multiple_images_and_renders_social_metadata(self):
        form = ArticleForm(
            data={
                "titre": "Un titre suffisamment long",
                "resume": "Un résumé de longueur suffisante pour l’article.",
                "contenu": "Un contenu suffisamment long pour respecter la validation de cet article.",
                "image_url": "",
                "statut": "publie",
                "images_to_delete": [],
            },
            files={
                "images": [
                    self.make_image("photo-1.png", "red"),
                    self.make_image("photo-2.png", "blue"),
                ]
            },
            instance=Article(auteur=self.user),
        )

        self.assertTrue(form.is_valid(), form.errors)
        article = form.save()

        self.assertEqual(ArticleImage.objects.filter(article=article).count(), 2)

        response = Client().get(
            reverse("articles:detail", kwargs={"slug": article.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 'name="twitter:card" content="summary_large_image"'
        )
        self.assertContains(response, 'property="og:type" content="article"')
        self.assertContains(
            response, 'property="og:url" content="https://journal.example/articles/'
        )
        self.assertContains(
            response,
            'property="og:image" content="https://journal.example/media/articles/',
        )
        for image in article.images.all():
            self.assertContains(response, image.image.url)


class CategoryManagementTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="journalist", password="pass")
        journalist_group, _ = Group.objects.get_or_create(name="Journalistes")
        self.user.groups.add(journalist_group)
        self.client.force_login(self.user)

    def test_journalist_can_create_category_without_creating_article(self):
        response = self.client.post(
            reverse("articles:gestion_categories"),
            {
                "nom": "Culture locale",
                "description": "Arts et événements de la région.",
                "couleur": "#2468ac",
            },
        )

        self.assertRedirects(
            response,
            reverse("articles:gestion_categories"),
            fetch_redirect_response=False,
        )
        self.assertTrue(Categorie.objects.filter(slug="culture-locale").exists())
        self.assertEqual(Article.objects.count(), 0)

        response = self.client.get(reverse("articles:gestion_categories"))
        self.assertContains(response, "Culture locale")

    def test_new_article_page_renders_category_modal(self):
        response = self.client.get(reverse("articles:creer_article"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="modalNouvelleCategorie"')
        self.assertContains(response, 'id="formNouvelleCategorie"')
        self.assertContains(response, 'action="/redaction/categories/creer/"')

    def test_modal_endpoint_returns_created_category_as_json(self):
        response = self.client.post(
            reverse("articles:creer_categorie_ajax"),
            {
                "nom": "Sciences et technologie",
                "description": "Actualités scientifiques.",
                "couleur": "#157347",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["nom"], "Sciences et technologie")
        self.assertTrue(
            Categorie.objects.filter(slug="sciences-et-technologie").exists()
        )
