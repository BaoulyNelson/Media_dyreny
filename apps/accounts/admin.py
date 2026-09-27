from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.utils.html import format_html
from .models import ProfilUtilisateur


# ═══════════════════════════════════════════════════════════
#  INLINE : afficher le profil directement dans la fiche User
# ═══════════════════════════════════════════════════════════

class ProfilInline(admin.StackedInline):
    model = ProfilUtilisateur
    can_delete = False
    verbose_name_plural = 'Profil'
    fields = ['bio', 'avatar', 'site_web', 'twitter']


# ═══════════════════════════════════════════════════════════
#  USER ADMIN — remplace le UserAdmin par défaut
#  avec les actions groupées directement sur la liste Users
# ═══════════════════════════════════════════════════════════

class UserAdmin(BaseUserAdmin):
    inlines = [ProfilInline]

    # Colonnes affichées
    list_display = [
        'username', 'email', 'first_name', 'last_name',
        'get_groupe', 'get_statut_actif', 'is_staff',
    ]
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'groups']

    # Actions groupées
    actions = [
        'accorder_droits_journaliste',
        'retirer_droits_journaliste',
        'activer_comptes',
        'desactiver_comptes',
    ]

    # ── Colonnes personnalisées ─────────────────────────────

    def get_groupe(self, obj):
        groupes = list(obj.groups.values_list('name', flat=True))
        if not groupes:
            return '—'
        return ', '.join(groupes)
    get_groupe.short_description = 'Groupe(s)'

    def get_statut_actif(self, obj):
        if obj.is_active:
            return format_html('<span style="color:#1a6638;font-weight:600;">✔ Actif</span>')
        return format_html('<span style="color:#9b1c2e;font-weight:600;">✘ Inactif</span>')
    get_statut_actif.short_description = 'Statut'

    # ── Actions groupées ────────────────────────────────────

    def accorder_droits_journaliste(self, request, queryset):
        groupe, _ = Group.objects.get_or_create(name='Journalistes')
        count = 0
        for user in queryset:
            user.groups.add(groupe)
            count += 1
        self.message_user(
            request,
            f"{count} utilisateur(s) ajouté(s) au groupe « Journalistes ».",
            messages.SUCCESS,
        )
    accorder_droits_journaliste.short_description = '✅ Accorder les droits Journaliste'

    def retirer_droits_journaliste(self, request, queryset):
        groupe = Group.objects.filter(name='Journalistes').first()
        if not groupe:
            self.message_user(request, "Le groupe « Journalistes » n'existe pas.", messages.WARNING)
            return
        count = 0
        for user in queryset:
            user.groups.remove(groupe)
            count += 1
        self.message_user(
            request,
            f"{count} utilisateur(s) retiré(s) du groupe « Journalistes ».",
            messages.SUCCESS,
        )
    retirer_droits_journaliste.short_description = '❌ Retirer les droits Journaliste'

    def activer_comptes(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} compte(s) activé(s).", messages.SUCCESS)
    activer_comptes.short_description = '🟢 Activer les comptes sélectionnés'

    def desactiver_comptes(self, request, queryset):
        updated = queryset.filter(is_superuser=False).update(is_active=False)
        ignores = queryset.filter(is_superuser=True).count()
        msg = f"{updated} compte(s) désactivé(s)."
        if ignores:
            msg += f" {ignores} superutilisateur(s) ignoré(s) par sécurité."
        self.message_user(request, msg, messages.WARNING)
    desactiver_comptes.short_description = '🔴 Désactiver les comptes sélectionnés'


# Désenregistrer l'UserAdmin par défaut et enregistrer le nôtre
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# ═══════════════════════════════════════════════════════════
#  PROFIL ADMIN — garde aussi les actions sur Profils
# ═══════════════════════════════════════════════════════════

@admin.register(ProfilUtilisateur)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'get_nom_complet', 'get_email', 'get_groupe', 'site_web', 'twitter']
    search_fields = ['utilisateur__username', 'utilisateur__first_name', 'utilisateur__last_name', 'bio']
    list_filter = ['utilisateur__groups', 'utilisateur__is_active']
    actions = [
        'accorder_droits_journaliste',
        'retirer_droits_journaliste',
        'activer_comptes',
        'desactiver_comptes',
        'vider_bio',
    ]

    def get_nom_complet(self, obj):
        return obj.get_nom_complet()
    get_nom_complet.short_description = 'Nom complet'

    def get_email(self, obj):
        return obj.utilisateur.email or '—'
    get_email.short_description = 'E-mail'

    def get_groupe(self, obj):
        groupes = list(obj.utilisateur.groups.values_list('name', flat=True))
        return ', '.join(groupes) if groupes else '—'
    get_groupe.short_description = 'Groupe(s)'

    def accorder_droits_journaliste(self, request, queryset):
        groupe, _ = Group.objects.get_or_create(name='Journalistes')
        count = 0
        for profil in queryset:
            profil.utilisateur.groups.add(groupe)
            count += 1
        self.message_user(request, f"{count} utilisateur(s) ajouté(s) au groupe « Journalistes ».", messages.SUCCESS)
    accorder_droits_journaliste.short_description = '✅ Accorder les droits Journaliste'

    def retirer_droits_journaliste(self, request, queryset):
        groupe = Group.objects.filter(name='Journalistes').first()
        if not groupe:
            self.message_user(request, "Le groupe « Journalistes » n'existe pas.", messages.WARNING)
            return
        count = 0
        for profil in queryset:
            profil.utilisateur.groups.remove(groupe)
            count += 1
        self.message_user(request, f"{count} utilisateur(s) retiré(s) du groupe « Journalistes ».", messages.SUCCESS)
    retirer_droits_journaliste.short_description = '❌ Retirer les droits Journaliste'

    def activer_comptes(self, request, queryset):
        ids = queryset.values_list('utilisateur_id', flat=True)
        updated = User.objects.filter(pk__in=ids).update(is_active=True)
        self.message_user(request, f"{updated} compte(s) activé(s).", messages.SUCCESS)
    activer_comptes.short_description = '🟢 Activer les comptes sélectionnés'

    def desactiver_comptes(self, request, queryset):
        ids = queryset.values_list('utilisateur_id', flat=True)
        updated = User.objects.filter(pk__in=ids, is_superuser=False).update(is_active=False)
        ignores = queryset.count() - updated
        msg = f"{updated} compte(s) désactivé(s)."
        if ignores:
            msg += f" {ignores} superutilisateur(s) ignoré(s) par sécurité."
        self.message_user(request, msg, messages.WARNING)
    desactiver_comptes.short_description = '🔴 Désactiver les comptes sélectionnés'

    def vider_bio(self, request, queryset):
        updated = queryset.update(bio='')
        self.message_user(request, f"Biographie effacée pour {updated} profil(s).", messages.SUCCESS)
    vider_bio.short_description = '🗑️ Effacer la biographie'