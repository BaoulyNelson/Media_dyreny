from django.contrib import admin
from .models import SiteConfiguration


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ("site_name", "email", "phone")
    fieldsets = (
        (
            "Identité du site",
            {"fields": ("site_name", "slogan", "site_description", "logo")},
        ),
        ("Coordonnées", {"fields": ("address", "phone", "email")}),
        (
            "Réseaux sociaux",
            {"fields": ("facebook_url", "twitter_url", "instagram_url", "youtube_url")},
        ),
    )


# ─── Header admin dynamique ────────────────────────────────────────────────
def get_dynamic_admin_context(original_each_context):
    def each_context(request):
        context = original_each_context(request)
        try:
            site_settings = SiteConfiguration.get_instance()
            if site_settings.site_name:
                context["site_header"] = f"Administration — {site_settings.site_name}"
                context["site_title"] = f"{site_settings.site_name} Admin"
        except Exception:
            # table pas encore créée (avant migrate) → on ignore silencieusement
            pass
        return context

    return each_context


admin.site.each_context = get_dynamic_admin_context(admin.site.each_context)
