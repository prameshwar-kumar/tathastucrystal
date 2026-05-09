from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Payment'),
        ('placed', 'Placed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('return_requested', 'Return Requested'),  # NEW
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    address = models.ForeignKey('account.Address', on_delete=models.PROTECT)
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    invoice_generated = models.BooleanField(default=False)
    stock_deducted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_id = models.PositiveIntegerField()
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    app_source = models.CharField(max_length=20, choices=(('crystal', 'Crystal'), ('worship', 'Worship')))

    @property
    def subtotal(self):
        return self.price * self.quantity
