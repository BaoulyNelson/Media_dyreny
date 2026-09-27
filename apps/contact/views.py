from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import ContactForm


class ContactView(FormView):
    template_name = 'contact/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact:succes')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Votre message a été envoyé avec succès. Nous vous répondrons dans les plus brefs délais.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titre_page'] = 'Nous contacter'
        return ctx


class ContactSuccesView(TemplateView):
    template_name = 'contact/succes.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titre_page'] = 'Message envoyé'
        return ctx
