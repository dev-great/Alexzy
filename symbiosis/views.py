from http.client import NOT_FOUND
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


class WalletDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_active:
            return Response({
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "message": "This account has been deactivated. Please contact the account administrator.",
                "error": "Bad Request"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Try to retrieve or create the wallet information
        try:
            wallet, created = WalletModel.objects.get_or_create(
                user=request.user)
        except WalletModel.DoesNotExist:
            return Response({
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "Data error.",
                "error": "Wallet information not found.",
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = WalletSerializer(wallet)
        return Response({
            "statusCode": status.HTTP_200_OK,
            "message": "Successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class TransactionHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            history = TransactionModel.objects.select_related(
                'user').filter(user=request.user)

        except Exception as e:
            return Response({
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Server error",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = TransactionSerializer(history, many=True)
        return Response({
            "statusCode": status.HTTP_200_OK,
            "message": "Successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=TransactionSerializer)
    def post(self, request):
        try:
            logged_in_user = request.user
            inshopper_user = CustomUser.objects.get(email=logged_in_user)

            serializer = TransactionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=inshopper_user)
                return Response({
                    "statusCode": status.HTTP_200_OK,
                    "message": "Successfully.",
                    "data": "Transaction created successfully"
                }, status=status.HTTP_200_OK)
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
