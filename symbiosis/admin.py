from django.contrib import admin

from .models import *
# Register your models here.


class WalletAdmin(admin. ModelAdmin):
    list_display = ("user_id", "balance", "created_on",)
    list_filter = ("balance", "created_on",)
    search_fields = ("user_id", "balance", "created_on",)


admin.site.register(WalletModel, WalletAdmin)


class TransactionsAdmin(admin. ModelAdmin):
    list_display = ("user_id", "amount", "title", "created_on",)
    list_filter = ("amount", "title", "created_on",)
    search_fields = ("user_id", "amount", "title", "created_on",)


admin.site.register(TransactionModel, TransactionsAdmin)
