from django.db import models


class MessageContact(models.Model):
    SUJET_CHOICES = [
        ('general', 'Question générale'),
        ('partenariat', 'Partenariat'),
        ('correction', 'Signaler une erreur'),
        ('presse', 'Relations presse'),
        ('autre', 'Autre'),
    ]

    nom = models.CharField(max_length=100, verbose_name="Nom complet")
    email = models.EmailField(verbose_name="Adresse e-mail")
    sujet = models.CharField(max_length=20, choices=SUJET_CHOICES, default='general', verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    date_envoi = models.DateTimeField(auto_now_add=True, verbose_name="Date d'envoi")
    traite = models.BooleanField(default=False, verbose_name="Traité")

    class Meta:
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering = ['-date_envoi']

    def __str__(self):
        return f"{self.nom} — {self.get_sujet_display()}"
