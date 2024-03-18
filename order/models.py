import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from order.choice import ORDER_STATUS_CHOICES

from products.models import Product

CustomUser = get_user_model()


class ShippingAddress(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    alternate_phone_number = models.CharField(
        max_length=20, blank=True, null=True)
    address_tag = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    additional_information = models.TextField(
        blank=True, null=True)
    delivery_address = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.city}, {self.state}"


class Order(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE)
    address = models.ForeignKey(ShippingAddress, on_delete=models.DO_NOTHING)
    total_price = models.FloatField(db_index=True)
    order_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=30, choices=ORDER_STATUS_CHOICES, default='PENDING_CONFIRMATION')
    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Order for {self.user} - Total Price: {self.total_price}"

    class Meta:
        ordering = ('-created_on',)


class OrderItem(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE)
    varient = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(db_index=True)
    price = models.FloatField(db_index=True)
    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Order: {self.order.id}, Product: {self.product.product_name}"

    class Meta:
        ordering = ('-created_on',)
