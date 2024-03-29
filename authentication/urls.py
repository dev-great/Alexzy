from django.urls import path, include
from .views import *
from rest_framework.authtoken.views import obtain_auth_token
from django.views.decorators.csrf import csrf_protect

app_name = 'authentication'

urlpatterns = [
    path('login/', csrf_protect(obtain_auth_token)),
    path('register/', RegisterView.as_view()),
    path('user_profile/', UserProfileView.as_view()),
    path('logout/', Logout.as_view()),
    path('changepassword/', ChangePasswordView.as_view()),
    path('delete_user/', DeleteAccount.as_view()),
    path('password_reset/', include('django_rest_passwordreset.urls')),
    path('referral_code/', ReferralView.as_view()),
    path('referral_history/', ReferralHistoryView.as_view()),
    path('user_kyc/', UserKYCView.as_view()),
    path('withdrawal_reset_otp/', OTPView.as_view()),
    path('withdrawal_reset_otp/verify/', OTPVerificationView.as_view()),

]
