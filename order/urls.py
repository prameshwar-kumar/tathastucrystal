from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('success/<str:order_number>/', views.order_success, name='order_success'),
    path('my-orders/', views.order_list, name='order_list'),

    path('invoice/<str:order_number>/', views.download_invoice, name='download_invoice'),
    path('cancel/<str:order_number>/', views.cancel_order, name='cancel_order'),
    path('return/<str:order_number>/', views.return_order, name='return_order'),
]
