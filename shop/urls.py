from django.urls import path
from .views import home, product, cart, checkout, success, stripe_webhook, add_to_cart, update_cart

urlpatterns = [
    path('', home, name='home'),
    path("product/", product, name='product'),
    path('cart/', cart, name='cart'),
    path('checkout/', checkout, name='checkout'),
    path('success/', success, name='success'),
    path('webhook/', stripe_webhook, name='stripe-webhook'),
    path('add_to_cart/<str:product_id>/', add_to_cart, name='add_to_cart'),
    path('update-cart/', update_cart, name='update_cart'),
]
