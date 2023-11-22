from http.client import NOT_FOUND
from authentication.models import ReferralCode
from order.models import OrderItem
from products.models import Product

from symbiosis.models import WalletModel
from .models import *
from .serializer import *
from django.db.models import Sum
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
# Create your views here.
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
User = get_user_model()


class CustomValidationException(Exception):
    def __init__(self, error, message, status_code=status.HTTP_400_BAD_REQUEST, *args, **kwargs):
        self.error = error,
        self.message = message,
        self.status_code = status_code
        super().__init__(*args, **kwargs)


class WithdrawlView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            withdrawals = WithdrawalModel.objects.filter(user=user)
            serializer = WithdrawalSerializer(withdrawals, many=True)
            return Response({
                "statusCode": status.HTTP_201_CREATED,
                "message": "Successfully.",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)
        except WithdrawalModel.DoesNotExist:
            return Response({
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "Data error.",
                "error": "No withdrawals found.",
            }, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Server error",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(request_body=WithdrawalSerializer)
    def post(self, request):
        logged_in_user = request.user
        try:
            user_balance = WalletModel.objects.get(user=logged_in_user)
        except CustomUser.DoesNotExist:
            return Response({
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "Data error.",
                "error": "User not found.",
            }, status=status.HTTP_404_NOT_FOUND
            )
        except WalletModel.DoesNotExist:
            return Response({
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "Data error.",
                "error": "User balance not found.",
            }, status=status.HTTP_404_NOT_FOUND
            )

        serializer = WithdrawalSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data.get("amount")
            if user_balance.balance >= amount:
                # Reduce the balance
                user_balance.balance -= amount
                user_balance.save()  # Save the updated balance

                # Save the withdrawal transaction
                serializer.save(user=user_balance.user)

                return Response({
                    "statusCode": status.HTTP_201_CREATED,
                    "message": "Successfully.",
                    "data": "Withdrawal successfully placed",
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "statusCode": status.HTTP_404_NOT_FOUND,
                    "message": "Data error.",
                    "error": "Insufficient balance.",
                }, status=status.HTTP_404_NOT_FOUND
                )
        return Response({
            "statusCode": status.HTTP_404_NOT_FOUND,
            "message": "Data error.",
            "error": serializer.errors,
        }, status=status.HTTP_404_NOT_FOUND
        )


class PaidCommision(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user_withdrawal_account = WithdrawalModel.objects.filter(
                user=request.user)
            total_amount = user_withdrawal_account.aggregate(Sum('amount'))[
                'amount__sum']
            if total_amount is None:
                total_amount = 0

            return Response({
                "statusCode": status.HTTP_200_OK,
                "message": "Total commission paid",
                "total_amount": total_amount,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "Data error.",
                "error": str(e),
            }, status=status.HTTP_404_NOT_FOUND)


class UserAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user_withdrawal_account = UserAccount.objects.filter(
                user=request.user)
            serializer = UserAccountSerializer(
                user_withdrawal_account, many=True)
            return Response({
                "statusCode": status.HTTP_200_OK,
                "message": "Successfully.",
                "data": serializer.data,
            }, status=status.HTTP_200_OK)
        except UserAccount.DoesNotExist:
            return Response({
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "Data error.",
                "error": "No user withdrawal accounts found.",
            }, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Server error",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(request_body=UserAccountSerializer)
    def post(self, request):
        try:
            logged_in_user = request.user

            serializer = UserAccountSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=logged_in_user)
                return Response({
                    "statusCode": status.HTTP_201_CREATED,
                    "message": "Successfully.",
                    "data": "User withdrawal account successfully added",
                }, status=status.HTTP_201_CREATED)
            return Response({
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "Data error.",
                "error": serializer.errors,
            }, status=status.HTTP_404_NOT_FOUND
            )
        except CustomUser.DoesNotExist:
            return Response({
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "Data error.",
                "error": "User not found.",
            }, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Server error",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CreatePaymentView(APIView):
    def post(self, request):
        serializer = PaymentSerializer(data=request.data)

        if serializer.is_valid():
            order_id = serializer.validated_data['order_id']
            amount = serializer.validated_data['amount']
            tranx_no = serializer.validated_data['tranx_no']
            referral_code = serializer.validated_data.get(
                'referral_code', None)

            user = request.user

            Payment.objects.create(
                user=user, amount=amount, tranx_no=tranx_no, order_id=order_id)

            referred_user = None
            if referral_code:
                try:
                    referred_user = ReferralCode.objects.get(
                        code=referral_code).user
                except ReferralCode.DoesNotExist:
                    referred_user = None

                # Loop through order items and accumulate commissions
                if referred_user and order_id:
                    order_items = OrderItem.objects.filter(order=order_id)

                    for order_item in order_items:
                        try:
                            product = order_item.product
                            quantity = order_item.quantity
                            commission = product.commission

                            total_commission = commission * quantity

                            wallet, created = WalletModel.objects.get_or_create(
                                user=referred_user)
                            wallet.balance += total_commission
                            wallet.save()
                        except Product.DoesNotExist:
                            pass

                return Response({'message': 'Payment created successfully'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
