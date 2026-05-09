from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import CartItem
from .utils import get_cart
from crystal.models import Product as CrystalProduct
from worship.models import Product as PujaProduct

def cart_detail(request):
    cart = get_cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})

@require_POST
def add_to_cart(request, app, product_id):
    cart = get_cart(request)
    product_model = CrystalProduct if app == 'crystal' else PujaProduct
    product = get_object_or_404(product_model, id=product_id)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1
    quantity = max(1, quantity)
    max_qty = product.stock if product.stock is not None else 99999
    quantity = min(quantity, max_qty)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product_id=product.id,
        app_source=app,
        defaults={
            'product_name': product.name,
            'price': product.discount_price or product.price,
            'image_url': product.main_image_url or '',
            'quantity': quantity,
        }
    )
    if not created:
        item.quantity = min(item.quantity + quantity, max_qty)
        item.save()

    if request.POST.get("buy_now") == "1":
        return redirect('order:checkout')
    return redirect('cart:cart_detail')


@require_POST
def update_cart(request, item_id, action):
    cart = get_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)

    product_model = CrystalProduct if item.app_source == 'crystal' else PujaProduct
    product = product_model.objects.filter(id=item.product_id).first()
    max_qty = product.stock if product and product.stock is not None else 99999

    if action == 'plus' and product:
        if item.quantity < max_qty:
            item.quantity += 1
    elif action == 'minus' and item.quantity > 1:
        item.quantity -= 1

    item.save()
    return redirect('cart:cart_detail')


@require_POST
def remove_from_cart(request, item_id):
    cart = get_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    return redirect('cart:cart_detail')
