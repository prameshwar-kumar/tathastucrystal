from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import Cart, CartItem
from crystal.models import Product as CrystalProduct
from worship.models import Product as PujaProduct

User = get_user_model()

class CartTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="test@example.com", password="123456")
        self.crystal_product = CrystalProduct.objects.create(
            name="Crystal Item", price=100, discount_price=80, stock=5, main_image_url=""
        )
        self.puja_product = PujaProduct.objects.create(
            name="Puja Item", price=200, discount_price=150, stock=3, main_image_url=""
        )

    def test_guest_add_to_cart(self):
        session = self.client.session
        session.save()
        self.client.post(f'/cart/add/crystal/{self.crystal_product.id}/', {'quantity': 2})
        cart = Cart.objects.get(session_key=session.session_key)
        self.assertEqual(cart.total_items, 2)
        self.assertEqual(cart.total_amount, 160)

    def test_quantity_limits_stock(self):
        session = self.client.session
        session.save()
        self.client.post(f'/cart/add/crystal/{self.crystal_product.id}/', {'quantity': 10})
        cart = Cart.objects.get(session_key=session.session_key)
        self.assertEqual(cart.total_items, 5)  # capped at stock

    def test_cart_merge_on_login(self):
        session = self.client.session
        session.save()
        guest_cart = Cart.objects.create(session_key=session.session_key)
        CartItem.objects.create(
            cart=guest_cart,
            product_id=self.crystal_product.id,
            product_name=self.crystal_product.name,
            price=self.crystal_product.discount_price,
            quantity=2,
            app_source='crystal'
        )
        self.client.login(email="test@example.com", password="123456")
        user_cart = Cart.objects.get(user=self.user)
        self.assertEqual(user_cart.total_items, 2)
        self.assertEqual(user_cart.total_amount, 160)

    def test_update_cart_plus_minus(self):
        cart = Cart.objects.create(user=self.user)
        item = CartItem.objects.create(
            cart=cart,
            product_id=self.crystal_product.id,
            product_name=self.crystal_product.name,
            price=self.crystal_product.discount_price,
            quantity=2,
            app_source='crystal'
        )
        self.client.post(f'/cart/update/{item.id}/plus/')
        item.refresh_from_db()
        self.assertEqual(item.quantity, 3)

        self.client.post(f'/cart/update/{item.id}/minus/')
        item.refresh_from_db()
        self.assertEqual(item.quantity, 2)

        self.client.post(f'/cart/update/{item.id}/minus/')
        self.client.post(f'/cart/update/{item.id}/minus/')
        item.refresh_from_db()
        self.assertEqual(item.quantity, 1)

    def test_remove_from_cart(self):
        cart = Cart.objects.create(user=self.user)
        item = CartItem.objects.create(
            cart=cart,
            product_id=self.crystal_product.id,
            product_name=self.crystal_product.name,
            price=self.crystal_product.discount_price,
            quantity=2,
            app_source='crystal'
        )
        self.client.post(f'/cart/remove/{item.id}/')
        self.assertEqual(cart.items.count(), 0)
