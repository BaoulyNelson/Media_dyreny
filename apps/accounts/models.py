from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class ProfilUtilisateur(models.Model):
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    bio = models.TextField(max_length=500, blank=True, verbose_name="Biographie")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Avatar")
    site_web = models.URLField(blank=True, verbose_name="Site web")
    twitter = models.CharField(max_length=100, blank=True, verbose_name="Twitter")

    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"

    def __str__(self):
        return f"Profil de {self.utilisateur.username}"

    def get_nom_complet(self):
        if self.utilisateur.first_name or self.utilisateur.last_name:
            return f"{self.utilisateur.first_name} {self.utilisateur.last_name}".strip()
        return self.utilisateur.username


@receiver(post_save, sender=User)
def creer_profil(sender, instance, created, **kwargs):
    if created:
        ProfilUtilisateur.objects.create(utilisateur=instance)


@receiver(post_save, sender=User)
def sauvegarder_profil(sender, instance, **kwargs):
    if hasattr(instance, 'profil'):
        instance.profil.save()
