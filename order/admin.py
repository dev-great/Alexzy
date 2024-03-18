from .models import *
from django.contrib import admin


class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'city', 'state')
    search_fields = ('user__email', 'first_name',
                     'last_name', 'city', 'state')


admin.site.register(ShippingAddress, ShippingAddressAdmin)


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'order_date')
    search_fields = ('user__username',)


admin.site.register(Order, OrderAdmin)


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price')
    search_fields = ('order__user__username', 'product__product_name')


admin.site.register(OrderItem, OrderItemAdmin)
