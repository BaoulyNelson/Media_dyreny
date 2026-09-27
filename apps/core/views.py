from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView

from .forms import SiteSettingsForm
from .models import SiteConfiguration


@method_decorator(staff_member_required, name="dispatch")
class SiteSettingsView(UpdateView):
    model = SiteConfiguration
    form_class = SiteSettingsForm
    template_name = "core/settings.html"
    success_url = "/parametres/"

    def get_object(self, queryset=None):
        return SiteConfiguration.get_instance()

    def form_valid(self, form):
        messages.success(
            self.request, "Les paramètres du site ont été enregistrés avec succès."
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titre_page"] = "Paramètres du site"
        return context
