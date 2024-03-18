import datetime
import random
from django.shortcuts import redirect
from django.conf import settings
from authentication.backend import EmailModelBackend
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .forms import CustomAuthenticationForm
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
from .models import *
from .serializer import *
from rest_framework import generics
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_protect
from rest_framework.generics import DestroyAPIView
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator
User = get_user_model()


class CustomValidationException(Exception):
    def __init__(self, error, message, status_code=status.HTTP_400_BAD_REQUEST, *args, **kwargs):
        self.error = error,
        self.message = message,
        self.status_code = status_code
        super().__init__(*args, **kwargs)


class RegisterView(APIView):
    csrf_protect_method = method_decorator(csrf_protect)

    @swagger_auto_schema(request_body=UserSerializer)
    def post(self, request):
        serializers = UserSerializer(data=request.data)
        if serializers.is_valid(raise_exception=True):
            email = serializers.validated_data.get("email")

            # Check if the email already exists
            if User.objects.filter(email=email).exists():
                return Response({
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "message": "This email address is already registered. If you forgot your password, you can reset it.",
                }, status=status.HTTP_400_BAD_REQUEST)

            # If email doesn't exist, save the new user
            user = serializers.save()

            # Create and associate a Token with the new user
            token, _ = Token.objects.get_or_create(user=user)

            # Include the token key in the payload

            try:
                data = ReferralCode.objects.select_related(
                    'user').get(user=user)
                if data is not None:
                    serializer_code = ReferralCodeSerializer(data)
                    payload = {
                        'user': serializers.data,
                        'token': token.key,
                        "referral_code": serializer_code.data,
                    }

            except ReferralCode.DoesNotExist:
                payload = {
                    'user': serializers.data,
                    'token': token.key,
                    "referral_code": None,
                }

            return Response({
                "statusCode": status.HTTP_200_OK,
                "message": "Registeration successful.",
                "data": payload,
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": status.HTTP_400_BAD_REQUEST,
            "message": "Invalid data.",
            "error": serializers.errors,
        }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    csrf_protect_method = method_decorator(csrf_protect)

    @swagger_auto_schema(request_body=UserSerializer)
    def patch(self, request):
        user_email = request.user.email
        profile = CustomUser.objects.get(email__exact=user_email)

        serializers = UserSerializer(
            profile, data=request.data, partial=True)
        if serializers.is_valid():

            # User update is sucessful
            serializers.save()
            return Response({
                "statusCode": status.HTTP_200_OK,
                "Success": "User updated successfully"
            },  status=status.HTTP_200_OK)

        # In an instance an error occures
        return Response({
            "statusCode": status.HTTP_400_BAD_REQUEST,
            "message": "Invalid data.",
            "error": serializers.errors,
        }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            email = request.user.email
            profile = CustomUser.objects.get(email__exact=email)
            serializer = UserSerializer(profile)
            try:
                data = ReferralCode.objects.select_related(
                    'user').get(user=self.request.user)
                if data is not None:
                    serializer_code = ReferralCodeSerializer(data)
                response_data = {
                    "profile": serializer.data,
                    "referral_code": serializer_code.data,

                }
            except ReferralCode.DoesNotExist:
                response_data = {
                    "profile": serializer.data,
                    "referral_code": None,
                }
            return Response({
                "statusCode": status.HTTP_200_OK,
                "message": "Success.",
                "data": response_data,
            }, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "message": "User profile not found.",
                "error": serializers.errors,
            }, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Invalid data.",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserLoginView(APIView):

    @swagger_auto_schema(request_body=UserLoginSerializer)
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        print("Before serializer.is_valid(raise_exception=True)")

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            # Login form validation error
            print("After serializer.is_valid(raise_exception=True), inside except block")
            return Response({
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "message": "An error occurred, validation failed.",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        print(f"{username} {password}")

        try:
            backend = EmailModelBackend()
            user = backend.authenticate(
                request, username=username, password=password)

            if user is not None and user.is_active:
                # User is active, generate token and return data
                try:
                    token, _ = Token.objects.get_or_create(user=user)
                    data = ReferralCode.objects.select_related(
                        'user').get(user=user)
                    if data is not None:
                        serializer_code = ReferralCodeSerializer(data)
                        payload = {
                            'token': token.key,
                            "referral_code": serializer_code.data,
                        }
                    else:
                        payload = {
                            'token': token.key,
                            "referral_code": "None",
                        }
                    return Response(payload, status=status.HTTP_200_OK)
                except Exception as e:
                    return Response({
                        "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "message": "An error occurred, data not fetched.",
                        "error": str(e)
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            elif user is not None and not user.is_active:
                # User account is not active
                return Response({
                    "statusCode": status.HTTP_403_FORBIDDEN,
                    "message": "This account has been deactivated. Please contact the account administrator.",
                }, status=status.HTTP_403_FORBIDDEN)
            else:
                # Invalid credentials
                return Response({
                    "statusCode": status.HTTP_401_UNAUTHORIZED,
                    "message": "Invalid credentials.",
                }, status=status.HTTP_401_UNAUTHORIZED)

        except ValidationError as e:
            # Handle validation errors raised by the authentication backend
            return Response({
                "statusCode": status.HTTP_403_FORBIDDEN,
                "message": str(e),
            }, status=status.HTTP_403_FORBIDDEN)


class Logout(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            request.user.auth_token.delete()
            return Response({
                "statusCode": status.HTTP_200_OK,
                "message": "Logged out successfully."
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "An error occurred while logging out.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = self.request.user
            old_password = serializer.data.get("old_password")
            new_password = serializer.data.get("new_password")

            if not user.check_password(old_password):
                return Response({
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "message": "Wrong password."
                }, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()

            return Response({
                "statusCode": status.HTTP_200_OK,
                "message": "Password updated successfully."
            }, status=status.HTTP_200_OK)

        return Response({
            "statusCode": status.HTTP_400_BAD_REQUEST,
            "message": "Invalid data.",
            "error": serializers.errors,
        }, status=status.HTTP_400_BAD_REQUEST)


class ReferralView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReferralCodeSerializer

    def get_object(self):
        try:
            return ReferralCode.objects.select_related('user').get(user=self.request.user)
        except ReferralCode.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is not None:
            serializer = self.serializer_class(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Referral code not found"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(request_body=ReferralCodeSerializer)
    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is not None:
            serializer = self.serializer_class(
                instance, data=request.data, partial=True, context={'request': request})
        else:
            serializer = self.serializer_class(
                data=request.data, context={'request': request})

        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        return Response({"error": False}, status=status.HTTP_201_CREATED)


class ReferralHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReferralHistorySerializer

    def get_queryset(self):
        return Referral.objects.filter(referred_by=self.request.user).select_related('referred_to')

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Referral.DoesNotExist:
            return Response({"error": "Referral history not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteAccount(DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return get_object_or_404(CustomUser, email=self.request.user.email)

    def delete(self, request, *args, **kwargs):
        try:
            inshopper_user = self.get_object()
            self.perform_destroy(inshopper_user)
            return Response({"result": "user deleted"}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserKYCView(APIView):
    permission_classes = [IsAuthenticated]
    csrf_protect_method = method_decorator(csrf_protect)

    @swagger_auto_schema(request_body=UserSerializer)
    def patch(self, request):
        user_email = request.user.email
        profile = CustomUser.objects.get(email__exact=user_email)
        wallet = WalletModel.objects.get(user=profile)

        # Update is_verified to True
        profile.is_verified = True

        # Subtract 50 from the wallet balance
        wallet.balance -= 80

        # Save changes
        profile.save()
        wallet.save()

        return Response({
            "statusCode": status.HTTP_200_OK,
            "Success": "User KYC updated successfully"
        },  status=status.HTTP_200_OK)


class OTPView(APIView):
    permission_classes = [IsAuthenticated]
    csrf_protect_method = method_decorator(csrf_protect)

    def post(self, request, *args, **kwargs):
        try:
            # Generate a random 4-digit OTP
            otp = str(random.randint(1000, 9999))

            # Set the OTP in the user's session
            user_profile = CustomUser.objects.get(email=request.user.email)
            user_profile.otp = otp
            user_profile.save()

            merge_data = {
                'inshopper_user': request.user.email,
                'otp': otp,
            }
            html_body = render_to_string(
                "emails/otp_mail.html", merge_data)
            msg = EmailMultiAlternatives(
                subject="Withdrawal Account Reset OTP.",
                from_email=settings.EMAIL_HOST_USER,
                to=[request.user.email],
                body=" ",  # Add a plain text alternative if needed
            )
            msg.attach_alternative(html_body, "text/html")
            msg.send(fail_silently=False)

            return Response({
                "statusCode": status.HTTP_200_OK,
                "Success": "OTP sent successfully"
            },  status=status.HTTP_200_OK)

        except Exception as e:
            # Handle the exception and return an error response
            return Response({
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Error": f"An error occurred: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OTPVerificationView(APIView):
    permission_classes = [IsAuthenticated]
    csrf_protect_method = method_decorator(csrf_protect)

    def post(self, request, *args, **kwargs):
        user_entered_otp = request.data.get('otp')

        user_profile = CustomUser.objects.get(email=request.user.email)
        stored_otp = user_profile.otp

        # Compare the user-entered OTP with the stored OTP
        if user_entered_otp == stored_otp:
            # OTP is valid, perform successful action
            return Response({
                "statusCode": status.HTTP_200_OK,
                "Success": "OTP verification successful"
            },  status=status.HTTP_200_OK)
        else:
            return Response({
                "statusCode": status.HTTP_404_NOT_FOUND,
                "error": "Invalid OTP."
            }, status=status.HTTP_404_NOT_FOUND)
