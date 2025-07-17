import stripe
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product, StripePrice

stripe.api_key = settings.STRIPE_SECRET_KEY

SUBSCRIPTION_INTERVALS = [1, 2, 3, 4, 6]

@receiver(post_save, sender=Product)
def create_stripe_data_for_product(sender, instance, created, **kwargs):
    print("Signal fired. Created:", created, instance.stripe_product_id)  # Add this first!
    if not created:
        return

    # Create Stripe Product
    if not instance.stripe_product_id:
        stripe_product = stripe.Product.create(name=instance.name)
        # instance.stripe_product_id = stripe_product.id
        # instance.save()
        Product.objects.filter(pk=instance.pk).update(stripe_product_id=stripe_product.id)
        instance.refresh_from_db()  # now instance has the real Stripe product ID
        print("Creating price for Stripe product ID:", instance.stripe_product_id)
        # One-Time Price
        price = stripe.Price.create(
            unit_amount=instance.price_cents,
            currency='usd',
            product=instance.stripe_product_id
        )
        StripePrice.objects.create(
            product=instance,
            stripe_price_id=price.id,
            one_time=True
        )

        # Subscription Prices
        for interval in SUBSCRIPTION_INTERVALS:
            price = stripe.Price.create(
                unit_amount=instance.price_cents,
                currency='usd',
                product=instance.stripe_product_id,
                recurring={'interval': 'month', 'interval_count': interval}
            )
            StripePrice.objects.create(
                product=instance,
                stripe_price_id=price.id,
                recurring_interval=interval,
                one_time=False
            )

# @receiver(post_save, sender=Product)
# def sync_stripe_product(sender, instance, created, **kwargs):
#     if created:
#         # Create Stripe product
#         stripe_product = stripe.Product.create(name=instance.name)
        
#         # Create Stripe price (one-time or recurring)
#         if instance.interval_months:
#             stripe_price = stripe.Price.create(
#                 unit_amount=instance.price_cents,
#                 currency='usd',
#                 recurring={"interval": "month", "interval_count": instance.interval_months},
#                 product=stripe_product.id
#             )
#         else:
#             stripe_price = stripe.Price.create(
#                 unit_amount=instance.price_cents,
#                 currency='usd',
#                 product=stripe_product.id
#             )

#         instance.stripe_product_id = stripe_product.id
#         instance.stripe_price_id = stripe_price.id
#         instance.save()

@receiver(post_delete, sender=Product)
def delete_stripe_product(sender, instance, **kwargs):
    if instance.stripe_product_id:
        stripe.Product.modify(instance.stripe_product_id, active=False)
