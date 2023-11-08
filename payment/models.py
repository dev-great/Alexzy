
from django.utils import timezone
import uuid
from django.db import models

from authentication.models import CustomUser
from products.models import Product

# Create your models here.


class Payment(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE)
    amount = models.DecimalField(
        default=0, max_digits=100, decimal_places=2)
    tranx_no = models.CharField(max_length=200)
    referral_code = models.CharField(max_length=20, null=True, blank=True)
    created_on = models.DateTimeField(default=timezone.now)


class UserAccount(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, default=None, db_index=True)
    acc_name = models.CharField(max_length=500)
    acc_number = models.CharField(max_length=500)
    bank_code = models.CharField(max_length=50)
    currency = models.CharField(max_length=10)

    class Meta:
        ordering = ('user',)


class WithdrawalModel(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, default=None, db_index=True)
    withdrawal_account = models.ForeignKey(
        UserAccount, on_delete=models.DO_NOTHING)
    amount = models.IntegerField(db_index=True)
    status = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_on',)
