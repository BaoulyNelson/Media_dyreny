from django import forms
from .models import Article, Comments


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


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['titre', 'categorie', 'tags', 'resume', 'contenu', 'image', 'image_url', 'statut', 'en_une']
        labels = {
            'titre': 'Titre',
            'categorie': 'Catégorie',
            'tags': 'Tags',
            'resume': 'Résumé (accroche)',
            'contenu': 'Contenu de l\'article',
            'image': 'Image principale (upload)',
            'image_url': 'OU lien image externe (URL)',
            'statut': 'Statut de publication',
            'en_une': 'Mettre à la une',
        }
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Titre accrocheur de l\'article...'
            }),
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.CheckboxSelectMultiple(),
            'resume': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Résumé court visible sur la page d\'accueil (max 500 caractères)...',
                'maxlength': '500',
            }),
            'contenu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 18,
                'placeholder': 'Rédigez votre article ici...',
                'id': 'id_contenu',
            }),
            'image_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://exemple.com/image.jpg'
            }),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'en_une': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_titre(self):
        titre = self.cleaned_data.get('titre', '').strip()
        if len(titre) < 10:
            raise forms.ValidationError("Le titre doit contenir au moins 10 caractères.")
        return titre

    def clean_resume(self):
        resume = self.cleaned_data.get('resume', '').strip()
        if len(resume) < 20:
            raise forms.ValidationError("Le résumé doit contenir au moins 20 caractères.")
        return resume

    def clean_contenu(self):
        contenu = self.cleaned_data.get('contenu', '').strip()
        if len(contenu) < 50:
            raise forms.ValidationError("Le contenu doit contenir au moins 50 caractères.")
        return contenu
