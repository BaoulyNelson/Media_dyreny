from django import forms
from .models import MessageContact


class ContactForm(forms.ModelForm):
    class Meta:
        model = MessageContact
        fields = ['nom', 'email', 'sujet', 'message']
        labels = {
            'nom': 'Nom complet',
            'email': 'Adresse e-mail',
            'sujet': 'Sujet',
            'message': 'Message',
        }
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom complet'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'votre@email.com'}),
            'sujet': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Décrivez votre demande en détail...'
            }),
        }

    def clean_message(self):
        msg = self.cleaned_data.get('message', '').strip()
        if len(msg) < 20:
            raise forms.ValidationError("Votre message doit contenir au moins 20 caractères.")
        return msg
