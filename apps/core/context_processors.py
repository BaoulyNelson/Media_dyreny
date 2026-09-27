from .models import SiteConfiguration


def site_settings_processor(request):
    return {"site_settings": SiteConfiguration.get_instance()}
