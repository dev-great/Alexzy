from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
User = get_user_model()


class WithdrawalSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = WithdrawalModel
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'


class UserAccountSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = UserAccount
        fields = '__all__'
