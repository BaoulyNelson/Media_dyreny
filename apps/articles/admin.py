from django.contrib import admin
from django.utils.html import format_html
from .models import Article, Categorie, Tag, Comments


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ["nom", "slug", "couleur_preview", "nombre_articles"]
    prepopulated_fields = {"slug": ("nom",)}

    def couleur_preview(self, obj):
        return format_html(
            '<div style="width:20px;height:20px;background:{};border-radius:3px;"></div>',
            obj.couleur,
        )

    couleur_preview.short_description = "Couleur"

    def nombre_articles(self, obj):
        return obj.nombre_articles()

    nombre_articles.short_description = "Articles publiés"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["nom", "slug"]
    prepopulated_fields = {"slug": ("nom",)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        "titre",
        "auteur",
        "categorie",
        "statut",
        "en_une",
        "vues",
        "date_publication",
    ]
    list_filter = ["statut", "en_une", "categorie", "date_publication"]
    search_fields = ["titre", "resume", "contenu"]
    prepopulated_fields = {"slug": ("titre",)}
    raw_id_fields = ["auteur"]
    date_hierarchy = "date_publication"
    list_editable = ["statut", "en_une"]
    filter_horizontal = ["tags"]
    fieldsets = (
        (
            "Informations principales",
            {"fields": ("titre", "slug", "auteur", "categorie", "tags")},
        ),
        ("Contenu", {"fields": ("resume", "contenu", "image", "image_url")}),
        ("Publication", {"fields": ("statut", "en_une", "date_publication")}),
    )

    def save_model(self, request, obj, form, change):
        if not obj.auteur_id:
            obj.auteur = request.user
        super().save_model(request, obj, form, change)


@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ["auteur", "article", "approuve", "date_creation"]
    list_filter = ["approuve", "date_creation"]
    list_editable = ["approuve"]
    search_fields = ["contenu", "auteur__username"]
    actions = ["approuver", "desapprouver"]

    def approuver(self, request, queryset):
        queryset.update(approuve=True)
        self.message_user(request, "Commentss approuvés.")

    approuver.short_description = "Approuver les Commentss sélectionnés"

    def desapprouver(self, request, queryset):
        queryset.update(approuve=False)
        self.message_user(request, "Commentss désapprouvés.")

    desapprouver.short_description = "Désapprouver les Commentss sélectionnés"
