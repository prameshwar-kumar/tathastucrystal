from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import now
from django.http import FileResponse
from django.conf import settings
from django.db import transaction
import os

from .models import Order, OrderItem
from payment.models import Payment
from cart.utils import get_cart
from account.models import Address
from order.utils import rollback_stock


@login_required
def checkout(request):
    cart = get_cart(request)
    if cart.total_items == 0:
        messages.error(request, "Your cart is empty.")
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        address_id = request.POST.get('address')
        address = get_object_or_404(Address, id=address_id, user=request.user)
        timestamp = int(now().timestamp())
        order_number = f"OD-{now().year}-{timestamp}"

        order = Order.objects.create(
            user=request.user,
            address=address,
            order_number=order_number,
            total_amount=cart.total_amount,
            status='pending'
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product_id=item.product_id,
                product_name=item.product_name,
                price=item.price,
                quantity=item.quantity,
                app_source=item.app_source
            )

        cart.items.all().delete()
        return redirect('payment:payment_select', order_id=order.id)

    addresses = Address.objects.filter(user=request.user)
    return render(request, 'order/checkout.html', {
        'cart': cart,
        'addresses': addresses,
        'total': cart.total_amount
    })


@login_required
def order_success(request, order_number):
    order = get_object_or_404(
        Order, order_number=order_number, user=request.user
    )
    return render(request, 'order/order_success.html', {'order': order})


@login_required
def order_list(request):
    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')
    return render(request, 'order/order_list.html', {'orders': orders})


@login_required
def download_invoice(request, order_number):
    order = get_object_or_404(
        Order,
        order_number=order_number,
        user=request.user,
        status__in=['placed', 'shipped', 'delivered', 'returned']
    )

    path = os.path.join(
        settings.MEDIA_ROOT,
        'invoices',
        f"{order.order_number}.pdf"
    )

    if not os.path.exists(path):
        messages.error(request, "Invoice not available.")
        return redirect('order:order_list')

    return FileResponse(
        open(path, 'rb'),
        as_attachment=True,
        filename=f"{order.order_number}.pdf"
    )


@login_required
def cancel_order(request, order_number):
    order = get_object_or_404(
        Order, order_number=order_number, user=request.user
    )

    # ❌ Cannot cancel after shipping or return
    if order.status in [
        'shipped', 'delivered', 'cancelled',
        'return_requested', 'returned'
    ]:
        messages.error(
            request,
            "Order cannot be cancelled at this stage."
        )
        return redirect('order:order_list')

    # ❌ BLOCK Razorpay PAID orders
    if hasattr(order, 'payment'):
        payment = order.payment
        if payment.method == 'razorpay' and payment.status == 'paid':
            messages.error(
                request,
                "Paid orders cannot be cancelled. "
                "Please request return after delivery."
            )
            return redirect('order:order_list')

    with transaction.atomic():
        order.status = 'cancelled'
        order.save(update_fields=['status'])
        rollback_stock(order)

    messages.success(request, "Order cancelled successfully.")
    return redirect('order:order_list')


@login_required
def return_order(request, order_number):
    order = get_object_or_404(
        Order, order_number=order_number, user=request.user
    )

    if order.status != 'delivered':
        messages.error(
            request,
            "Return not allowed for this order."
        )
        return redirect('order:order_list')

    order.status = 'return_requested'
    order.save(update_fields=['status'])

    messages.success(
        request,
        "Return request submitted. Admin will review it."
    )
    return redirect('order:order_list')
