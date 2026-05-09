import json, hmac, hashlib, logging
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from django.db import transaction
from .models import Payment
from order.utils import deduct_stock, generate_invoice

logger = logging.getLogger(__name__)

@csrf_exempt
def razorpay_webhook(request):
    signature = request.headers.get('X-Razorpay-Signature')
    body = request.body

    if not signature:
        logger.warning("Razorpay webhook missing signature")
        return HttpResponse(status=400)

    expected = hmac.new(
        settings.RAZORPAY_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        logger.warning("Invalid Razorpay webhook signature")
        return HttpResponse(status=400)

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        logger.error("Invalid JSON payload")
        return HttpResponse(status=400)

    event = payload.get('event')
    if event not in ['payment.captured', 'refund.processed']:
        return HttpResponse(status=200)

    entity = payload['payload']['payment']['entity']
    order_id = entity.get('order_id')
    payment_id = entity.get('id')

    if not order_id or not payment_id:
        logger.error("Webhook missing order_id or payment_id")
        return HttpResponse(status=400)

    try:
        with transaction.atomic():
            payment = Payment.objects.select_for_update().get(
                razorpay_order_id=order_id
            )
            order = payment.order

            # ✅ PAYMENT SUCCESS
            if event == 'payment.captured' and payment.status != 'paid':
                if payment.status != 'paid':
                    payment.status = 'paid'
                    payment.razorpay_payment_id = payment_id
                    payment.save(update_fields=['status', 'razorpay_payment_id'])

                if order.status != 'placed':
                    order.status = 'placed'
                    order.save(update_fields=['status'])

                deduct_stock(order)

                if not order.invoice_generated:
                    generate_invoice(order)
                    order.invoice_generated = True
                    order.save(update_fields=['invoice_generated'])

            # ✅ REFUND CONFIRMATION (NO STOCK CHANGE HERE)
            elif event == 'refund.processed':
                if payment.status != 'refunded':
                    payment.status = 'refunded'
                    payment.save(update_fields=['status'])

                if order.status != 'returned':
                    order.status = 'returned'
                    order.save(update_fields=['status'])

    except Payment.DoesNotExist:
        logger.error(f"Payment not found for Razorpay order_id: {order_id}")
        return HttpResponse(status=404)

    except Exception as e:
        logger.exception(f"Webhook processing error: {e}")
        return HttpResponse(status=500)

    return HttpResponse(status=200)
