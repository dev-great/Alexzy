from django.urls import path
from .views import *

app_name = 'symbiosis'

urlpatterns = [
    path('wallet/', WalletDetailView.as_view()),
    path('transactions/', TransactionHistoryView.as_view()),
]
