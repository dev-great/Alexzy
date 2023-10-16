import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

from products.models import Product

CustomUser = get_user_model()


class Cart(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='CartItem')

    def get_total_quantity(self):
        return sum(item.quantity for item in self.cart_items.all())

    def get_total_price(self):
        return sum(item.get_subtotal() for item in self.cart_items.all())

    def __str__(self):
        return f"Cart for {self.user}"


class CartItem(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='cart_items', db_index=True)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    price = models.FloatField(db_index=True)
    created_on = models.DateTimeField(default=timezone.now)

    def get_subtotal(self):
        if self.negotiated_price is not None:
            return self.negotiated_price * self.quantity
        return self.price * self.quantity

    def __str__(self):
        return f"CartItem: {self.product} - Quantity: {self.quantity}"
