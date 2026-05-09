from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.conf import settings
from django.db import transaction
import os

from crystal.models import Product as CrystalProduct
from worship.models import Product as WorshipProduct

def generate_invoice(order):
    invoice_dir = os.path.join(settings.MEDIA_ROOT, 'invoices')
    os.makedirs(invoice_dir, exist_ok=True)
    file_path = os.path.join(invoice_dir, f"{order.order_number}.pdf")

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "INVOICE")
    y -= 40

    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Order Number: {order.order_number}")
    c.drawString(350, y, f"Date: {order.created_at.strftime('%d-%m-%Y')}")

    y -= 25
    c.drawString(50, y, f"Customer: {order.user.username}")

    y -= 30
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Item")
    c.drawString(350, y, "Amount")

    y -= 20
    c.setFont("Helvetica", 10)
    for item in order.items.all():
        subtotal = item.price * item.quantity
        c.drawString(50, y, f"{item.product_name} (x{item.quantity})")
        c.drawString(350, y, f"₹ {subtotal}")
        y -= 18

    y -= 20
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, f"Total Amount: ₹ {order.total_amount}")

    c.showPage()
    c.save()
    return file_path


@transaction.atomic
def deduct_stock(order):
    if order.stock_deducted:
        return
    for item in order.items.select_for_update():
        model = CrystalProduct if item.app_source == 'crystal' else WorshipProduct
        product = model.objects.select_for_update().get(id=item.product_id)
        product.stock -= item.quantity
        product.save(update_fields=['stock'])
    order.stock_deducted = True
    order.save(update_fields=['stock_deducted'])


@transaction.atomic
def rollback_stock(order):
    if not order.stock_deducted:
        return
    for item in order.items.select_for_update():
        model = CrystalProduct if item.app_source == 'crystal' else WorshipProduct
        product = model.objects.select_for_update().get(id=item.product_id)
        product.stock += item.quantity
        product.save(update_fields=['stock'])
    order.stock_deducted = False
    order.save(update_fields=['stock_deducted'])

from django.db import transaction

@transaction.atomic
def mark_order_delivered(order):
    """
    Final delivery handler:
    - Marks order delivered
    - Marks COD payment as paid
    """

    if order.status == 'delivered':
        return  # idempotent safety

    order.status = 'delivered'
    order.save(update_fields=['status'])

    # ✅ COD payment becomes PAID ONLY after delivery
    if hasattr(order, 'payment'):
        payment = order.payment

        if payment.method == 'cod' and payment.status != 'paid':
            payment.status = 'paid'
            payment.save(update_fields=['status'])
