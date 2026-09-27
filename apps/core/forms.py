from django import forms
from .models import SiteConfiguration


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteConfiguration
        fields = [
            "site_name",
            "slogan",
            "site_description",
            "logo",
            "address",
            "phone",
            "email",
            "facebook_url",
            "twitter_url",
            "instagram_url",
            "youtube_url",
        ]
        labels = {
            "site_name": "Nom du site",
            "slogan": "Slogan",
            "site_description": "Description du site",
            "logo": "Logo du site",
            "address": "Adresse",
            "phone": "Téléphone",
            "email": "E-mail",
            "facebook_url": "Lien Facebook",
            "twitter_url": "Lien X / Twitter",
            "instagram_url": "Lien Instagram",
            "youtube_url": "Lien YouTube",
        }
        widgets = {
            "site_name": forms.TextInput(attrs={"class": "form-control"}),
            "slogan": forms.TextInput(attrs={"class": "form-control"}),
            "site_description": forms.Textarea(
                attrs={"class": "form-control", "rows": 4}
            ),
            "logo": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "facebook_url": forms.URLInput(attrs={"class": "form-control"}),
            "twitter_url": forms.URLInput(attrs={"class": "form-control"}),
            "instagram_url": forms.URLInput(attrs={"class": "form-control"}),
            "youtube_url": forms.URLInput(attrs={"class": "form-control"}),
        }
