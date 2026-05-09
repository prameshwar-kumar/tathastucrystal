from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL

class Cart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cart",
    )
    session_key = models.CharField(max_length=40, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_amount(self):
        total = sum((item.subtotal for item in self.items.all()), Decimal("0.00"))
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product_id = models.PositiveIntegerField()
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    image_url = models.URLField(blank=True)

    app_source = models.CharField(
        max_length=20,
        choices=(('crystal', 'Crystal'), ('worship', 'Worship'))
    )

    @property
    def subtotal(self):
        subtotal = Decimal(self.price) * Decimal(self.quantity)
        return subtotal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    class Meta:
        indexes = [
            models.Index(fields=['cart', 'product_id', 'app_source']),
        ]
