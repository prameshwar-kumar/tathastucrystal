from .utils import get_cart

def cart_context(request):
    """
    Provides global template variables:
    - cart_count: total number of items in the cart
    - cart_total: total amount of the cart
    """
    try:
        cart = get_cart(request)
        return {
            'cart_count': cart.total_items if cart else 0,
            'cart_total': cart.total_amount if cart else 0
        }
    except Exception:
        return {
            'cart_count': 0,
            'cart_total': 0
        }
