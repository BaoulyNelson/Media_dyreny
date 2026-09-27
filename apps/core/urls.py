from django.urls import path
from .views import SiteSettingsView

app_name = "core"

urlpatterns = [
    path("parametres/", SiteSettingsView.as_view(), name="settings"),
]
