from django.contrib import admin

# Register your models here.
from .models import Product, Order, StripePrice, SEOPage

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_cents', 'get_subscription_intervals', 'get_stripe_price_ids')

    def get_subscription_intervals(self, obj):
        intervals = StripePrice.objects.filter(product=obj, one_time=False).values_list('recurring_interval', flat=True)
        return ', '.join(f"{i} mo" for i in intervals)
    get_subscription_intervals.short_description = 'Subscription Intervals'

    def get_stripe_price_ids(self, obj):
        prices = StripePrice.objects.filter(product=obj).values_list('stripe_price_id', flat=True)
        return ', '.join(prices)
    get_stripe_price_ids.short_description = 'Stripe Price IDs'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('email', 'amount_paid', 'quantity', 'interval_months', 'created_at')

@admin.register(SEOPage)
class SEOPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('title',)}