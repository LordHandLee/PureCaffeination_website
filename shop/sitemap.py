from django.contrib.sitemaps import Sitemap
from .models import SEOPage

class SEOPageSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return SEOPage.objects.all()

    def location(self, obj):
        return f'/pages/{obj.slug}/'
