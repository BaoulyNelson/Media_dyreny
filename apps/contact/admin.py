from django.contrib import admin
from .models import MessageContact


@admin.register(MessageContact)
class MessageContactAdmin(admin.ModelAdmin):
    list_display = ['nom', 'email', 'sujet', 'date_envoi', 'traite']
    list_filter = ['sujet', 'traite', 'date_envoi']
    list_editable = ['traite']
    search_fields = ['nom', 'email', 'message']
    readonly_fields = ['date_envoi']
