from django.urls import path
from . import views
from .webhooks import razorpay_webhook

app_name = 'payment'

urlpatterns = [
    path('select/<int:order_id>/', views.payment_select, name='payment_select'),
    path('razorpay/verify/', views.razorpay_verify, name='razorpay_verify'),
    path('razorpay/webhook/', razorpay_webhook, name='razorpay_webhook'),
    path('failed/', views.payment_failed, name='payment_failed'),
    path('retry/', views.payment_retry, name='payment_retry'),
]
