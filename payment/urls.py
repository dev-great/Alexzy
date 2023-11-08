from django.urls import path, include
from .views import *
from rest_framework.authtoken.views import obtain_auth_token
from django.views.decorators.csrf import csrf_protect

app_name = 'wallet'

urlpatterns = [
    path('user_account/', UserAccountView.as_view()),
    path('withdrawal/', WithdrawlView.as_view()),
    path('create-payment/', CreatePaymentView.as_view(), name='create-payment'),
]
