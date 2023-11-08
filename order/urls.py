from django.urls import path
from .views import *

app_name = 'order'

urlpatterns = [
    path('shipping-address/', ShippingAddressAPIView.as_view(),
         name='shipping-address'),
    path('orders/', OrderAPIView.as_view(), name='orders'),
]
