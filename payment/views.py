from decimal import Decimal
from http.client import NOT_FOUND
import logging
import secrets
import string
from django.db.models import F
from django.conf import settings
from authentication.models import ReferralCode
from order.models import OrderItem
from products.models import Product
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

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
        secret_key = "sk_live_2fca85d7db7f4b363473c2b7c11ef19858fa8bb9"
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
                user=request.user).first()
            serializer = UserAccountSerializer(user_withdrawal_account)
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
    def delete(self, request, *args, **kwargs):
        try:
            logged_in_user = request.user
            user_withdrawal_account = UserAccount.objects.filter(
                user=logged_in_user).first()
            user_withdrawal_account.delete()

            return Response({
                "statusCode": status.HTTP_204_NO_CONTENT,
                "message": "Successfully deleted user withdrawal account.",
            }, status=status.HTTP_204_NO_CONTENT)

        except UserAccount.DoesNotExist:
            return Response({
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "User withdrawal account not found.",
                "error": "User withdrawal account not found.",
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Server error",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

            self.send_purchase_receipt_email(user, order_id)
            if referral_code:
                try:
                    referred_user = ReferralCode.objects.get(
                        code=referral_code).user
                except ReferralCode.DoesNotExist:
                    referred_user = None

                if order_id:
                    order_items = OrderItem.objects.filter(order=order_id)
                    for order_item in order_items:
                        try:
                            product = order_item.product
                            quantity = order_item.quantity
                            commission = product.commission
                            total_commission = commission * quantity
                            Product.objects.filter(id=product.id).update(
                                quantity=F('quantity') - quantity)
                            if referred_user:
                                wallet, created = WalletModel.objects.get_or_create(
                                    user=referred_user)
                                wallet.balance += total_commission
                                wallet.save()
                                TransactionModel.objects.create(
                                    user=referred_user,
                                    amount=total_commission,
                                    currency="NGN",
                                    reference=''.join(secrets.choice(
                                        string.ascii_letters + string.digits) for _ in range(20)),
                                    source="balance",
                                    source_details=None,
                                    reason="Commission",
                                    status="success",
                                    failures=None,
                                    transfer_code=''.join(secrets.choice(
                                        string.ascii_letters + string.digits) for _ in range(20)),
                                    titan_code=None,
                                    transferred_at=None,
                                    integration=None,
                                    request=None,
                                    recipient=None,
                                )

                        except Exception as e:
                            return JsonResponse({"error": f"An error occurred: {e}"}, status=500)
                print(f"order_id: {order_id}")
                self.send_purchase_receipt_email(order_id.id, referred_user)
                return Response({'message': 'Payment created successfully'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_purchase_receipt_email(self, order_id, referred_user):
        try:
            print(f"order_id: {order_id}")
            order = Order.objects.get(id=order_id)
            order_items = OrderItem.objects.filter(order=order)

            if referred_user is None:
                subject = "Alexzy Purchase Receipt"
                referred_user = None
                referred_email = None
            else:
                print(f"referred_user: {referred_user}")
                referral = CustomUser.objects.get(email=referred_user)
                subject = "Alexzy Purchase Receipt (Agent Referred)"
                referred_user = f"{referral.first_name} {referral.last_name}"
                referred_email = f"{referral.email}"

            merge_data = {
                'order': order,
                'order_items': order_items,
                'delivery_address': order.address,
                'referred_user': referred_user,
                'referred_email': referred_email,
            }
            html_body = render_to_string(
                "emails/product_alert.html", merge_data)
            msg = EmailMultiAlternatives(
                subject=subject,
                from_email=settings.EMAIL_HOST_USER,
                to=["sales@alexzypolska.com"],
                body=" ",
            )
            msg.attach_alternative(html_body, "text/html")
            msg.send(fail_silently=False)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"An error occurred: {e}", exc_info=True)
            return JsonResponse({"error": "An internal server error occurred."}, status=500)


def paystack_bank_view(request):
    secret_key = "sk_live_2fca85d7db7f4b363473c2b7c11ef19858fa8bb9"
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

    transfer_charge = calculate_transfer_charge(amount)

    secret_key = "sk_live_2fca85d7db7f4b363473c2b7c11ef19858fa8bb9"
    # secret_key = "sk_test_8337c0f651e13e01151760e7d9b9f645238ca3e0"
    url = "https://api.paystack.co/transfer"
    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json",
    }

    try:
        user_account = UserAccount.objects.get(id=withdrawal_account_id)

        if (Decimal(f"{amount}")/100) <= 9000000:

            if user_balance.balance >= (Decimal(f"{amount}")/100) + transfer_charge:

                data = {
                    "source": "balance",
                    "reason": reason,
                    "amount": Decimal(f"{amount}"),
                    "recipient": user_account.recipient_code,
                }

                response = requests.post(url, headers=headers, json=data)

                if response.status_code == 200:
                    transfer_code = response.json().get("data", {}).get("transfer_code")

                    data = response.json().get("data", {})
                    TransactionModel.objects.create(
                        user=request.user,
                        amount=f"{data.get('amount') / 100}",
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

                    user_balance.balance -= ((data.get("amount") /
                                             100) + transfer_charge)
                    user_balance.save()

                    try:
                        merge_data = {
                            'user': request.user,
                            'amount': data.get("amount")/100,
                            'transfer_code': data.get("transfer_code"),
                            "status": data.get("status"),
                        }
                        html_body = render_to_string(
                            "emails/payment.html", merge_data)
                        msg = EmailMultiAlternatives(
                            subject="Agent Withdrawal Placed.",
                            from_email=settings.EMAIL_HOST_USER,
                            to=[request.user.email],
                            body=" ",
                        )
                        msg.attach_alternative(html_body, "text/html")
                        msg.send(fail_silently=False)
                    except Exception as e:
                        logger = logging.getLogger(__name__)
                        logger.error(f"An error occurred: {e}", exc_info=True)

                    return Response({
                        "statusCode": status.HTTP_200_OK,
                        "message": response.json().get("message")
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
        else:
            return Response({
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "Data error.",
                "error": "You cannot withdraw more than ₦9,000,000 at a time.",
            }, status=status.HTTP_404_NOT_FOUND)

    except UserAccount.DoesNotExist:
        return Response("UserAccount not found", status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        # Handle exceptions
        print("Exception during Paystack Transfer API call:", str(e))
        return Response("Internal Server Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def calculate_transfer_charge(amount):
    if (Decimal(amount) /
            100) <= 5000:
        return 10
    elif 5001 <= (Decimal(amount) /
                  100) <= 50000:
        return 25
    else:
        return 50
# @api_view(['POST'])
# def resend_paystack_otp(request):
#     secret_key = "sk_live_2fca85d7db7f4b363473c2b7c11ef19858fa8bb9"

#     url = "https://api.paystack.co/transfer/resend_otp"
#     headers = {
#         "Authorization": f"Bearer {secret_key}",
#         "Content-Type": "application/json",
#     }

#     data = {
#         "transfer_code": request.data.get("transfer_code"),
#         "reason": "transfer",
#     }

#     try:
#         response = requests.post(url, headers=headers, json=data)
#         print("Paystack Resend OTP API Response Status Code:", response.status_code)
#         print("Paystack Resend OTP API Response Content:", response.text)

#         if response.status_code == 200:
#             return Response({"message": "OTP resend successful."}, status=status.HTTP_200_OK)
#         else:
#             # Handle Paystack API errors if needed
#             return Response(response.text, status=response.status_code)

#     except Exception as e:
#         # Handle exceptions
#         print("Exception during Paystack Resend OTP API call:", str(e))
#         return Response("Internal Server Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def finalize_paystack_transfer(request):
#     logged_in_user = request.user
#     user_balance = WalletModel.objects.get(user=logged_in_user)
#     transfer_code = request.data.get('transfer_code')
#     otp = request.data.get('otp')

#     secret_key = "sk_live_2fca85d7db7f4b363473c2b7c11ef19858fa8bb9"
#     url = "https://api.paystack.co/transfer/finalize_transfer"
#     headers = {
#         "Authorization": f"Bearer {secret_key}",
#         "Content-Type": "application/json",
#     }

#     data = {
#         "transfer_code": transfer_code,
#         "otp": otp,
#     }

#     try:
#         response = requests.post(url, headers=headers, json=data)
#         print("Paystack Finalize Transfer API Response Status Code:",
#               response.status_code)
#         print("Paystack Finalize Transfer API Response Content:", response.text)

#         if response.status_code == 200:

#             data = response.json().get("data", {})
#             TransactionModel.objects.create(
#                 user=request.user,
#                 amount=data.get("amount"),
#                 currency=data.get("currency"),
#                 reference=data.get("reference"),
#                 source=data.get("source"),
#                 source_details=data.get("source_details"),
#                 reason=data.get("reason"),
#                 status=data.get("status"),
#                 failures=data.get("failures"),
#                 transfer_code=data.get("transfer_code"),
#                 titan_code=data.get("titan_code"),
#                 transferred_at=data.get("transferred_at"),
#                 integration=data.get("integration"),
#                 request=data.get("request"),
#                 recipient=data.get("recipient"),
#             )

#             user_balance.balance -= data.get("amount")
#             user_balance.save()
#             return Response(response.json(), status=status.HTTP_200_OK)
#         else:

#             return Response(response.text, status=response.status_code)

#     except Exception as e:
#         print("Exception during Paystack Finalize Transfer API call:", str(e))
#         return Response("Internal Server Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_and_update_transaction_status(request):
    try:
        latest_transaction = TransactionModel.objects.filter(
            user=request.user).first()

        if latest_transaction.status == 'success' or latest_transaction.status == 'Commission':
            # Do nothing if the latest transaction is already successful
            return Response({
                "statusCode": status.HTTP_200_OK,
                "message": "Latest transaction is already successful."
            }, status=status.HTTP_200_OK)

        reference_code = latest_transaction.reference
       # secret_key = "sk_live_2fca85d7db7f4b363473c2b7c11ef19858fa8bb9"
        secret_key = "sk_test_8337c0f651e13e01151760e7d9b9f645238ca3e0"
        verify_url = f"https://api.paystack.co/transfer/verify/{reference_code}"
        headers = {
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json",
        }

        verify_response = requests.get(verify_url, headers=headers)

        if verify_response.status_code == 200:
            verify_data = verify_response.json().get("data", {})
            print(verify_data)
            paystack_status = verify_data.get("status")
            print(paystack_status)

            # Update the transaction status based on Paystack response
            latest_transaction.status = paystack_status
            latest_transaction.save()

            return Response({
                "statusCode": status.HTTP_200_OK,
                "message": "Transaction status updated based on Paystack response."
            }, status=status.HTTP_200_OK)
        else:
            # Handle Paystack API verification errors if needed
            return Response(verify_response.text, status=verify_response.status_code)

    except TransactionModel.DoesNotExist:
        return Response("No transactions found for the user.", status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        # Handle exceptions
        print("Exception during transaction status check:", str(e))
        return Response("Internal Server Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
