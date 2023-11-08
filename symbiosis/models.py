import uuid
from django.db import models

from authentication.models import CustomUser

# Create your models here.


class TransactionModel(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, default=None, db_index=True)
    amount = models.IntegerField(default=0)
    title = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_on',)


class WalletModel(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, default=None, db_index=True)
    balance = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_on',)
