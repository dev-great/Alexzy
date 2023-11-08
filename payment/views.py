from http.client import NOT_FOUND
from authentication.models import ReferralCode

from symbiosis.models import WalletModel
from .models import *
from .serializer import *

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
            product = serializer._validated_data['product']
            amount = serializer.validated_data['amount']
            tranx_no = serializer.validated_data['tranx_no']
            referral_code = serializer.validated_data.get(
                'referral_code', None)

            user = request.user

            Payment.objects.create(
                user=user, amount=amount, tranx_no=tranx_no, product=product)

            referred_user = None
            if referral_code:
                try:
                    referred_user = ReferralCode.objects.get(
                        code=referral_code)
                except CustomUser.DoesNotExist:
                    referred_user = None

                # Add commission from Product model if there's a referral and a product
                if referred_user:
                    try:
                        # You need to define the logic for this
                        product = Product.objects.get(id=product.id)
                        # Assuming 'commission' is a field in the Product model
                        commission = product.commission

                        # Create or update the user's wallet with the commission amount
                        wallet, created = WalletModel.objects.get_or_create(
                            user=referred_user.user)
                        wallet.balance += commission
                        wallet.save()
                    except Product.DoesNotExist:
                        pass

                return Response({'message': 'Payment created successfully'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
