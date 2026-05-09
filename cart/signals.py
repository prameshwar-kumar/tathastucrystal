from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from .merge import merge_guest_cart_to_user

@receiver(user_logged_in)
def merge_cart_after_login(sender, request, user, **kwargs):
    merge_guest_cart_to_user(request, user)
