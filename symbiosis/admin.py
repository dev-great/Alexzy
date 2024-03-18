from django.contrib import admin

from .models import *
# Register your models here.


class WalletAdmin(admin. ModelAdmin):
    list_display = ("user_id", "balance", "created_on",)
    list_filter = ("balance", "created_on",)
    search_fields = ("user_id", "balance", "created_on",)


admin.site.register(WalletModel, WalletAdmin)


class TransactionsAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'amount', 'currency', 'reference',
        'source', 'reason', 'status', 'transfer_code',
        'transferred_at', 'created_at', 'updated_at'
    )
    list_filter = ('status', 'currency')
    search_fields = ('reference', 'reason', 'transfer_code')


admin.site.register(TransactionModel, TransactionsAdmin)
