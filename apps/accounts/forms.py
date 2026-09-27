from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from .models import ProfilUtilisateur


class ConnexionForm(AuthenticationForm):
    username = forms.CharField(
        label="Nom d'utilisateur ou e-mail",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Nom d'utilisateur ou e-mail",
                "autofocus": True,
            }
        ),
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Mot de passe"}
        ),
    )

    error_messages = {
        "invalid_login": "Nom d'utilisateur/e-mail ou mot de passe incorrect. Veuillez réessayer.",
        "inactive": "Ce compte est désactivé.",
    }

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username and "@" in username:
            user = User.objects.filter(email__iexact=username).first()
            if user:
                return user.username
        return username


class StyledPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="Adresse e-mail",
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Adresse e-mail",
                "autofocus": True,
            }
        ),
    )


class StyledSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Nouveau mot de passe",
                "autofocus": True,
            }
        )
        self.fields["new_password2"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Confirmer le nouveau mot de passe",
            }
        )


class InscriptionForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Adresse e-mail",
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Adresse e-mail"}
        ),
    )
    first_name = forms.CharField(
        max_length=50,
        required=False,
        label="Prénom",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Prénom"}
        ),
    )
    last_name = forms.CharField(
        max_length=50,
        required=False,
        label="Nom",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Nom de famille"}
        ),
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]
        labels = {"username": "Nom d'utilisateur"}
        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nom d'utilisateur"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Mot de passe"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Confirmer le mot de passe"}
        )
        self.fields["password1"].label = "Mot de passe"
        self.fields["password2"].label = "Confirmer le mot de passe"
        self.fields["password1"].help_text = (
            "Au moins 8 caractères, avec des lettres et des chiffres."
        )
        self.fields["password2"].help_text = ""

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cette adresse e-mail est déjà utilisée.")
        return email


class ProfilForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50,
        required=False,
        label="Prénom",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    last_name = forms.CharField(
        max_length=50,
        required=False,
        label="Nom",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        required=True,
        label="Adresse e-mail",
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = ProfilUtilisateur
        fields = ["bio", "avatar", "site_web", "twitter"]
        labels = {
            "bio": "Biographie",
            "avatar": "Photo de profil",
            "site_web": "Site web",
            "twitter": "Compte Twitter",
        }
        widgets = {
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "avatar": forms.ClearableFileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "site_web": forms.URLInput(attrs={"class": "form-control"}),
            "twitter": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "@votre_compte"}
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email
