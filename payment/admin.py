from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'order',
        'method',
        'status',
        'order_amount',
        'razorpay_payment_id',
        'created_at',
    )

    list_filter = ('method', 'status')
    search_fields = ('order__order_number', 'razorpay_payment_id')

    readonly_fields = (
        'order',
        'method',
        'order_amount',
        'razorpay_order_id',
        'razorpay_payment_id',
        'razorpay_signature',
        'created_at',
    )

    fields = (
        'order',
        'method',
        'status',
        'order_amount',
        'razorpay_order_id',
        'razorpay_payment_id',
        'razorpay_signature',
        'created_at',
    )

    def order_amount(self, obj):
        return obj.order.total_amount

    order_amount.short_description = "Amount"

    def has_delete_permission(self, request, obj=None):
        return False
