from django.urls import path
from .views import *

app_name = 'order'

urlpatterns = [
    path('cart/', CartAPIView.as_view(), name='cart'),
    path('cart_items/', CartItemsView.as_view(), name='cart'),
]
