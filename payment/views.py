import logging
import razorpay
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db import transaction
from order.utils import generate_invoice, deduct_stock
from order.models import Order
from .models import Payment
from .razorpay_service import create_razorpay_order

logger = logging.getLogger(__name__)

@login_required
def payment_select(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if request.method == 'POST':
        method = request.POST.get('payment_method')

        if method == 'cod':
            with transaction.atomic():
                Payment.objects.update_or_create(
                    order=order,
                    defaults={'method': 'cod', 'status': 'initiated','amount': order.total_amount}

                )
                if order.status != 'placed':
                    order.status = 'placed'
                    order.save(update_fields=['status'])
                deduct_stock(order)
                if not order.invoice_generated:
                    try:
                        generate_invoice(order)
                    except Exception as e:
                        raise RuntimeError("Invoice generation failed")

                    order.invoice_generated = True
                    order.save(update_fields=['invoice_generated'])

            return redirect('order:order_success', order_number=order.order_number)

        if method == 'razorpay':
            rzp_order = create_razorpay_order(order.total_amount, order.order_number)
            Payment.objects.update_or_create(order=order, defaults={'method':'razorpay','razorpay_order_id':rzp_order['id'],'status':'initiated','amount': order.total_amount})
            return render(request, 'payment/razorpay_start.html', {'order':order,'razorpay_key':settings.RAZORPAY_KEY_ID,'razorpay_order_id':rzp_order['id'],'amount':int(order.total_amount*100),'callback_url':request.build_absolute_uri('/payment/razorpay/verify/')})

    return render(request, 'payment/payment_select.html', {'order': order})


@csrf_exempt
def razorpay_verify(request):
    if request.method != 'POST':
        return redirect('/')
    data = request.POST
    try:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        client.utility.verify_payment_signature({'razorpay_order_id':data.get('razorpay_order_id'),'razorpay_payment_id':data.get('razorpay_payment_id'),'razorpay_signature':data.get('razorpay_signature')})

        with transaction.atomic():
            payment = Payment.objects.select_for_update().get(razorpay_order_id=data.get('razorpay_order_id'))
            order = payment.order

            if payment.status != 'paid':
                payment.razorpay_payment_id = data.get('razorpay_payment_id')
                payment.razorpay_signature = data.get('razorpay_signature')
                payment.status = 'paid'
                payment.save(update_fields=['razorpay_payment_id','razorpay_signature','status'])

            if order.status != 'placed':
                order.status = 'placed'
                order.save(update_fields=['status'])

            deduct_stock(order)
            if not order.invoice_generated:
                try:
                    generate_invoice(order)
                except Exception as e:
                    raise RuntimeError("Invoice generation failed")

                order.invoice_generated = True
                order.save(update_fields=['invoice_generated'])

        return redirect('order:order_success', order_number=order.order_number)
    except Exception as e:
        logger.exception(f"Razorpay verify failed: {e}")
        Payment.objects.filter(
            razorpay_order_id=data.get('razorpay_order_id'),
            status__in=['initiated', 'authorized']
        ).update(status='failed')
        messages.error(request, "Payment verification failed")
        return redirect('payment:payment_failed')


def payment_failed(request):
    return render(request,'payment/payment_failed.html')


def payment_retry(request):
    return render(request,'payment/payment_retry.html')
