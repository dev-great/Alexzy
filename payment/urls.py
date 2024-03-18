from django.urls import path, include
from .views import *
from rest_framework.authtoken.views import obtain_auth_token
from django.views.decorators.csrf import csrf_protect

app_name = 'wallet'

urlpatterns = [
    path('user_account/', UserAccountView.as_view()),
    path('create-payment/', CreatePaymentView.as_view(), name='create-payment'),
    path('paid-commission/', PaidCommision.as_view(), name='paid-commission'),
    path('paystack/bank/', paystack_bank_view, name='paystack_bank'),
    path('paystack/initiate_paystack_transfer/',
         initiate_paystack_transfer, name='initiate_paystack_transfer'),
    #     path('paystack/finalize_paystack_transfer/',
    #          finalize_paystack_transfer, name='finalize_paystack_transfer'),
    path('paystack/update_transaction_status/',
         check_and_update_transaction_status, name='update_transaction_status'),
]
