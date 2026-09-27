from django.db import models


class SiteConfiguration(models.Model):
    site_name = models.CharField(
        max_length=120, default="Le Média", verbose_name="Nom du site"
    )
    slogan = models.CharField(
        max_length=200, default="L'info qui compte", verbose_name="Slogan"
    )
    site_description = models.TextField(
        blank=True,
        default="Plateforme d’information, d’analyses et de reportages.",
        verbose_name="Description du site",
    )
    logo = models.ImageField(
        upload_to="site/", blank=True, null=True, verbose_name="Logo du site"
    )
    address = models.CharField(max_length=255, blank=True, verbose_name="Adresse")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Téléphone")
    email = models.EmailField(blank=True, verbose_name="E-mail")
    facebook_url = models.URLField(blank=True, verbose_name="Lien Facebook")
    twitter_url = models.URLField(blank=True, verbose_name="Lien X / Twitter")
    instagram_url = models.URLField(blank=True, verbose_name="Lien Instagram")
    youtube_url = models.URLField(blank=True, verbose_name="Lien YouTube")

    class Meta:
        verbose_name = "Paramètre du site"
        verbose_name_plural = "Paramètres du site"

    def __str__(self):
        return self.site_name

    @classmethod
    def get_instance(cls):
        instance, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                "site_name": "Le Média",
                "slogan": "L'info qui compte",
                "site_description": "Plateforme d’information, d’analyses et de reportages.",
            },
        )
        return instance
