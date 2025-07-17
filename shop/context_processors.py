from django.conf import settings

def site_theme(request):
    return {'theme': getattr(settings, 'SITE_THEME', 'brand')}
