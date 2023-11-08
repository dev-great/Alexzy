from django.contrib import admin

from .models import *
# Register your models here.


class UserAccountAdmin(admin. ModelAdmin):
    list_display = ("user", "acc_name",
                    "acc_number", "bank_code", "currency")
    search_fields = ("user", "acc_type", "bank_code", "acc_name", "currency")


admin.site.register(UserAccount, UserAccountAdmin)


class WithdrawalAdmin(admin. ModelAdmin):
    list_display = ("user_id", "amount", "created_on",)
    list_filter = ("amount", "created_on",)
    search_fields = ("user_id", "amount", "created_on",)


admin.site.register(WithdrawalModel, WithdrawalAdmin)


class PaymentAdmin(admin. ModelAdmin):
    list_display = ("user", "amount", "tranx_no", "created_on",)
    search_fields = ("user", "amount", "tranx_no", "created_on",)


admin.site.register(Payment, PaymentAdmin)
