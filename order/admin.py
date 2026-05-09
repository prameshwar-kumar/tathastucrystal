from django.contrib import admin
import razorpay
from django.conf import settings

from .models import Order, OrderItem
from .utils import mark_order_delivered, rollback_stock


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        'product_name',
        'price',
        'quantity',
        'app_source'
    )


@admin.action(description="Mark Selected Orders as Delivered")
def mark_as_delivered(modeladmin, request, queryset):
    for order in queryset.select_related('payment'):
        if order.status in ['placed', 'shipped']:
            mark_order_delivered(order)


@admin.action(description="Approve Return Requests")
def approve_return(modeladmin, request, queryset):
    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    for order in queryset.filter(
        status='return_requested',
        payment__method='razorpay',
        payment__status='paid'
        ):
        order.status = 'returned'
        order.save(update_fields=['status'])

        # 🔁 Restore stock
        rollback_stock(order)

        # 🔁 Razorpay refund
        if hasattr(order, 'payment') and order.payment.method == 'razorpay':
            payment = order.payment
            if payment.method == 'razorpay' and payment.status == 'paid':
                if payment.razorpay_payment_id:
                    client.payment.refund(
                        payment.razorpay_payment_id,
                        {
                            "amount": int(float(order.total_amount) * 100),
                            "speed": "optimum"
                        }
                    )
                    payment.status = 'refunded'
                    payment.save(update_fields=['status'])

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number',
        'user',
        'status',
        'total_amount',
        'created_at',
    )

    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'user__email')
    inlines = [OrderItemInline]

    # 🔒 UNEDITABLE FIELDS
    readonly_fields = (
        'order_number',
        'user',
        'address',
        'total_amount',
        'created_at',
    )

    # 🧭 Control what appears in admin form
    fields = (
        'order_number',
        'user',
        'address',
        'status',
        'total_amount',
        'created_at',
    )

    actions = [
        mark_as_delivered,
        approve_return,
    ]