from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
User = get_user_model()


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletModel
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = TransactionModel
        fields = '__all__'
