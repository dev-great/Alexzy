import uuid
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from authentication.models import CustomUser
from django.db.models.signals import post_save
from django.dispatch import receiver


class TransactionModel(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, default=None, db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    reference = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    source_details = models.CharField(max_length=255, null=True, blank=True)
    reason = models.CharField(max_length=255)
    status = models.CharField(max_length=20)
    failures = models.CharField(max_length=255, null=True, blank=True)
    transfer_code = models.CharField(max_length=255, null=True, blank=True)
    titan_code = models.CharField(max_length=255, null=True, blank=True)
    transferred_at = models.DateTimeField(null=True, blank=True)
    integration = models.IntegerField(null=True, blank=True)
    request = models.IntegerField(null=True, blank=True)
    recipient = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transaction {self.id}"

    class Meta:
        ordering = ('-updated_at',)


class WalletModel(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, default=None, db_index=True)
    balance = models.PositiveBigIntegerField(default=0)
    withdrawal_status = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_on',)
