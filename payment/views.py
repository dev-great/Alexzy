from http.client import NOT_FOUND
import secrets
import string
from authentication.models import ReferralCode
from order.models import OrderItem
from products.models import Product

from symbiosis.models import TransactionModel, WalletModel
from .models import *
from .serializer import *

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
import requests
from django.http import JsonResponse
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
# Create your views here.
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Sum

from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
User = get_user_model()


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


class CustomValidationException(Exception):
    def __init__(self, error, message, status_code=status.HTTP_400_BAD_REQUEST, *args, **kwargs):
        self.error = error,
        self.message = message,
        self.status_code = status_code
        super().__init__(*args, **kwargs)


class UserAccountView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=UserAccountSerializer)
    def post(self, request):
        try:
            logged_in_user = request.user
            serializer = UserAccountSerializer(data=request.data)
            if serializer.is_valid():
                user_account = serializer.save(user=logged_in_user)
                recipient_code = self.create_paystack_transfer_recipient(
                    user_account)
                print(f"This is my code: {recipient_code}")
                user_account.recipient_code = recipient_code
                user_account.save()
                return Response({
                    "statusCode": status.HTTP_201_CREATED,
                    "message": "Successfully added user withdrawal account.",
                    "data": {
                        "user_account_id": str(user_account.id),
                        "recipient_code": recipient_code,
                    },
                }, status=status.HTTP_201_CREATED)

            return Response({
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "message": "Data validation error.",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        except CustomUser.DoesNotExist:
            return Response({
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "User not found.",
                "error": "User not found.",
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Server error",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create_paystack_transfer_recipient(self, user_account):
        secret_key = "sk_test_76e31bb10f4963267329d7922780eb3be2e1f19e"
        url = "https://api.paystack.co/transferrecipient"
        headers = {
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json",
        }
        data = {
            "type": "nuban",
            "name": user_account.acc_name,
            "account_number": user_account.acc_number,
            "bank_code": user_account.bank_code,
            "currency": user_account.currency,
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            print(response)
            if response.status_code == 201:
                created_recipient = response.json()
                return created_recipient.get("data", {}).get("recipient_code")
            else:
                # Handle Paystack API errors if needed
                return None
        except Exception as e:
            # Handle exceptions
            return None

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

                # Add commission from Product model if there's a referral and a product
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
                            TransactionModel.objects.create(
                                user=request.user,
                                amount=commission,
                                currency="NGN",
                                reference=''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(20)),
                                source="balance",
                                source_details=None,
                                reason="Commission",
                                status="success",
                                failures=None,
                                transfer_code=''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(20)),
                                titan_code=None,
                                transferred_at=None,
                                integration=None,
                                request=None,
                                recipient=None,
                            )
                        except Exception as e:
                             return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

                return Response({'message': 'Payment created successfully'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def paystack_bank_view(request):
    secret_key = "sk_test_76e31bb10f4963267329d7922780eb3be2e1f19e"
    url = "https://api.paystack.co/bank"
    headers = {
        "Authorization": f"Bearer {secret_key}",
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            refined_data = [
                {
                    "name": bank["name"],
                    "code": bank["code"],
                    "currency": bank["currency"],
                }
                for bank in data.get("data", [])
            ]

            return JsonResponse({"data": refined_data}, safe=False)
        else:
            return JsonResponse({"error": f"Request failed with status code {response.status_code}"}, status=response.status_code)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_paystack_transfer(request):
    logged_in_user = request.user
    user_balance = WalletModel.objects.get(user=logged_in_user)
    withdrawal_account_id = request.data.get('withdrawal_account_id')
    reason = request.data.get('reason')
    amount = request.data.get('amount')

    secret_key = "sk_test_76e31bb10f4963267329d7922780eb3be2e1f19e"
    url = "https://api.paystack.co/transfer"
    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json",
    }

    try:
        # Fetch UserAccount object based on withdrawal_id
        user_account = UserAccount.objects.get(id=withdrawal_account_id)

        data = {
            "source": "balance",
            "reason": reason,
            "amount": f"{amount}00",
            "recipient": user_account.recipient_code,
        }
        if user_balance.balance >= (int(amount)/100):
            response = requests.post(url, headers=headers, json=data)
            print("Paystack Transfer API Response Status Code:",
                  response.status_code)
            print("Paystack Transfer API Response Content:", response.text)

            if response.status_code == 200:
                transfer_code = response.json().get("data", {}).get("transfer_code")
                return Response({
                    "transfer_code": transfer_code
                }, status=status.HTTP_200_OK)
            else:
                # Handle Paystack API errors if needed
                return Response(response.text, status=response.status_code)
        else:
            return Response({
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "Data error.",
                "error": "Insufficient balance.",
            }, status=status.HTTP_404_NOT_FOUND)

    except UserAccount.DoesNotExist:
        return Response("UserAccount not found", status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        # Handle exceptions
        print("Exception during Paystack Transfer API call:", str(e))
        return Response("Internal Server Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def finalize_paystack_transfer(request):
    logged_in_user = request.user
    user_balance = WalletModel.objects.get(user=logged_in_user)
    transfer_code = request.data.get('transfer_code')
    otp = request.data.get('otp')

    secret_key = "sk_test_76e31bb10f4963267329d7922780eb3be2e1f19e"
    url = "https://api.paystack.co/transfer/finalize_transfer"
    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json",
    }

    data = {
        "transfer_code": transfer_code,
        "otp": otp,
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        print("Paystack Finalize Transfer API Response Status Code:",
              response.status_code)
        print("Paystack Finalize Transfer API Response Content:", response.text)

        if response.status_code == 200:

            data = response.json().get("data", {})
            TransactionModel.objects.create(
                user=request.user,
                amount=data.get("amount"),
                currency=data.get("currency"),
                reference=data.get("reference"),
                source=data.get("source"),
                source_details=data.get("source_details"),
                reason=data.get("reason"),
                status=data.get("status"),
                failures=data.get("failures"),
                transfer_code=data.get("transfer_code"),
                titan_code=data.get("titan_code"),
                transferred_at=data.get("transferred_at"),
                integration=data.get("integration"),
                request=data.get("request"),
                recipient=data.get("recipient"),
            )

            user_balance.balance -= data.get("amount")
            user_balance.save()
            return Response(response.json(), status=status.HTTP_200_OK)
        else:

            return Response(response.text, status=response.status_code)

    except Exception as e:
        print("Exception during Paystack Finalize Transfer API call:", str(e))
        return Response("Internal Server Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
