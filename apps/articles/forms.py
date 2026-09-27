from html import unescape

import nh3
from django import forms
from django.utils.html import strip_tags
from django.utils.text import slugify
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Article, ArticleImage, Categorie, Comments


class CommentsForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ["contenu"]
        labels = {"contenu": "Votre Comments"}
        widgets = {
            "contenu": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Partagez votre avis sur cet article...",
                    "class": "form-control",
                    "maxlength": "1000",
                }
            )
        }

    def clean_contenu(self):
        contenu = self.cleaned_data.get("contenu", "").strip()
        if len(contenu) < 10:
            raise forms.ValidationError(
                "Votre Comments doit contenir au moins 10 caractères."
            )
        if len(contenu) > 1000:
            raise forms.ValidationError(
                "Votre Comments ne peut pas dépasser 1000 caractères."
            )
        return contenu


class RechercheForm(forms.Form):
    q = forms.CharField(
        label="Rechercher",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Rechercher un article...",
                "class": "form-control",
            }
        ),
    )


class MultipleImageInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    widget = MultipleImageInput

    def clean(self, data, initial=None):
        if not data:
            return []
        files = data if isinstance(data, (list, tuple)) else [data]
        return [super(MultipleImageField, self).clean(file, initial) for file in files]


class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ["nom", "description", "couleur"]
        labels = {
            "nom": "Nom de la catégorie",
            "description": "Description",
            "couleur": "Couleur",
        }
        widgets = {
            "nom": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ex. Culture"}
            ),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "couleur": forms.TextInput(
                attrs={"class": "form-control form-control-color", "type": "color"}
            ),
        }

    def clean_nom(self):
        nom = self.cleaned_data["nom"].strip()
        slug = slugify(nom)
        if Categorie.objects.filter(slug=slug).exists():
            raise forms.ValidationError(
                "Une catégorie avec ce nom ou une URL équivalente existe déjà."
            )
        return nom


class ArticleForm(forms.ModelForm):
    images = MultipleImageField(
        required=False,
        label="Ajouter des images",
        widget=MultipleImageInput(
            attrs={"class": "form-control", "accept": "image/*", "id": "gallery-upload"}
        ),
    )
    images_to_delete = forms.ModelMultipleChoiceField(
        queryset=ArticleImage.objects.none(),
        required=False,
        label="Images à supprimer",
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Article
        fields = [
            "titre",
            "categorie",
            "tags",
            "resume",
            "contenu",
            "image",
            "image_url",
            "statut",
            "en_une",
            "images",
            "images_to_delete",
        ]
        labels = {
            "titre": "Titre",
            "categorie": "Catégorie",
            "tags": "Tags",
            "resume": "Résumé (accroche)",
            "contenu": "Contenu de l'article",
            "image": "Image principale (upload)",
            "image_url": "OU lien image externe (URL)",
            "statut": "Statut de publication",
            "en_une": "Mettre à la une",
        }
        widgets = {
            "titre": forms.TextInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "Titre accrocheur de l'article...",
                }
            ),
            "categorie": forms.Select(attrs={"class": "form-select"}),
            "tags": forms.CheckboxSelectMultiple(),
            "resume": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Résumé proposé automatiquement depuis le contenu.",
                    "maxlength": "500",
                    "id": "id_resume",
                }
            ),
            "contenu": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="default"
            ),
            "image": forms.ClearableFileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "image_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://exemple.com/image.jpg",
                }
            ),
            "statut": forms.Select(attrs={"class": "form-select"}),
            "en_une": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["resume"].required = False
        if self.instance.pk:
            self.fields["images_to_delete"].queryset = self.instance.images.all()

    def clean_images(self):
        images = self.cleaned_data.get("images", [])
        if len(images) > 10:
            raise forms.ValidationError(
                "Vous pouvez ajouter jusqu’à 10 images à la fois."
            )
        return images

    def save(self, commit=True):
        article = super().save(commit=commit)
        if commit:
            self.save_gallery(article)
        return article

    def save_gallery(self, article):
        for image in self.cleaned_data.get("images_to_delete", []):
            image.image.delete(save=False)
            image.delete()

        last_position = (
            article.images.order_by("-position")
            .values_list("position", flat=True)
            .first()
        )
        position = (last_position if last_position is not None else -1) + 1
        for uploaded_image in self.cleaned_data.get("images", []):
            ArticleImage.objects.create(
                article=article,
                image=uploaded_image,
                position=position,
            )
            position += 1

    def clean_titre(self):
        titre = self.cleaned_data.get("titre", "").strip()
        if len(titre) < 10:
            raise forms.ValidationError(
                "Le titre doit contenir au moins 10 caractères."
            )
        return titre

    def clean_resume(self):
        resume = self.cleaned_data.get("resume", "").strip()
        if resume and len(resume) < 20:
            raise forms.ValidationError(
                "Le résumé doit contenir au moins 20 caractères."
            )
        return resume

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("resume") and cleaned_data.get("contenu"):
            text = " ".join(unescape(strip_tags(cleaned_data["contenu"])).split())
            resume = text[:500].strip()
            if len(resume) < 20:
                self.add_error(
                    "resume",
                    "Le contenu est trop court pour générer un résumé automatiquement.",
                )
            else:
                cleaned_data["resume"] = resume
        return cleaned_data

    def clean_contenu(self):
        contenu = self.cleaned_data.get("contenu", "").strip()
        text = " ".join(unescape(strip_tags(contenu)).split())
        if len(text) < 50:
            raise forms.ValidationError(
                "Le contenu doit contenir au moins 50 caractères."
            )
        return nh3.clean(
            contenu,
            tags={
                "p",
                "br",
                "strong",
                "b",
                "em",
                "i",
                "u",
                "s",
                "del",
                "a",
                "h2",
                "h3",
                "h4",
                "blockquote",
                "ul",
                "ol",
                "li",
                "hr",
            },
            attributes={"a": {"href", "title", "target"}},
            url_schemes={"http", "https", "mailto"},
        )
