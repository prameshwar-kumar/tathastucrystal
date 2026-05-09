from .models import Cart, CartItem
from crystal.models import Product as CrystalProduct
from worship.models import Product as PujaProduct

def merge_guest_cart_to_user(request, user):
    """
    Merge guest cart into logged-in user cart, enforcing stock limits.
    """
    guest_session_key = request.session.get("guest_session_key")
    if not guest_session_key:
        return

    try:
        guest_cart = Cart.objects.get(session_key=guest_session_key)
    except Cart.DoesNotExist:
        return

    user_cart, _ = Cart.objects.get_or_create(user=user)

    for guest_item in guest_cart.items.all():
        product_model = CrystalProduct if guest_item.app_source == 'crystal' else PujaProduct
        product = product_model.objects.filter(id=guest_item.product_id).first()
        max_qty = product.stock if product and product.stock is not None else 99999

        user_item, created = CartItem.objects.get_or_create(
            cart=user_cart,
            product_id=guest_item.product_id,
            app_source=guest_item.app_source,
            defaults={
                "product_name": guest_item.product_name,
                "price": guest_item.price,
                "quantity": min(guest_item.quantity, max_qty),
                "image_url": guest_item.image_url,
            },
        )
        if not created:
            user_item.quantity = min(user_item.quantity + guest_item.quantity, max_qty)
            user_item.save()

    guest_cart.delete()
    request.session.pop("guest_session_key", None)
