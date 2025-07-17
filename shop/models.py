from django.db import models

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=255)
    price_cents = models.PositiveIntegerField()  # e.g., 499 for $4.99
    description = models.TextField()
    stripe_product_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - ${self.price_cents / 100:.2f}"
    


class Order(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=255)
    address = models.JSONField()  # stores shipping address dict from Stripe
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_session_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    quantity = models.IntegerField(default=1)
    interval_months = models.IntegerField(default=1)  # For subscriptions
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - ${self.amount_paid} ({self.quantity} bottles every {self.interval_months} months)"


    # def __str__(self):
    #     return f"{self.email} - ${self.amount_paid}"

class Signup(models.Model):
    email = models.EmailField(unique=True)
    joined_at = models.DateTimeField(auto_now_add=True)

class StripePrice(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stripe_prices')
    stripe_price_id = models.CharField(max_length=255, unique=True)
    recurring_interval = models.PositiveIntegerField(null=True, blank=True)  # e.g., 1, 2, 3, 4 months
    one_time = models.BooleanField(default=False)

    class Meta:
        unique_together = ('product', 'recurring_interval', 'one_time')

    def __str__(self):
        if self.one_time:
            return f"{self.product.name} (One-Time)"
        else:
            return f"{self.product.name} (Every {self.recurring_interval} mo)"
