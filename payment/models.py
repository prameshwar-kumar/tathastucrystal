from django.db import models
from order.models import Order

class Payment(models.Model):
    METHOD_CHOICES = (('cod', 'Cash On Delivery'), ('razorpay', 'Razorpay'))
    STATUS_CHOICES = (('initiated', 'Initiated'), ('authorized', 'Authorized'), ('paid', 'Paid'), ('failed', 'Failed'), ('refunded', 'Refunded'))

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order.order_number} - {self.method}"
