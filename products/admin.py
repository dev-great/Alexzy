from .models import *
from django.contrib import admin
from django.utils.html import format_html

# Register your models here.


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'product_name', 'category', 'brand', 'online_presence', 'short_description',
                    'ram', 'storage', 'processor', 'screen_size', 'touch_screen', 'backlight_keyboard', 'convertible', 'webcam', 'dedicated_video_ram', 'graphics_card', 'condition', 'battery_life')
    list_filter = ('online_presence', 'condition', 'brand', 'category')
    search_fields = ("user_id__username", "product_name", 'online_presence',
                     'ram', 'storage', 'processor', 'screen_size', 'condition', 'battery_life')

    def short_description(self, obj):
        max_length = 50
        if len(obj.description) > max_length:
            return obj.description[:max_length] + '...'
        return obj.description

    short_description.short_description = 'Description'  # Column header in admin


admin.site.register(Product, ProductAdmin)


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'image_display',)
    search_fields = ("product_id", )

    readonly_fields = ('image_preview',)

    def image_display(self, obj):
        return format_html('<img src="{}" width="110" height="100" />', obj.image.url)

    def image_preview(self, obj):
        return format_html('<img src="{}" width="50" height="50" />', obj.image.url)

    image_display.short_description = 'Primary Image'
    image_preview.short_description = 'Primary Image Preview'


admin.site.register(ProductImage, ProductImageAdmin)


admin.site.register(ProductCategory)
admin.site.register(ProductBrand)
admin.site.register(ProductColor)
admin.site.register(Filter)
admin.site.register(BestSeller)
admin.site.register(Testimonial)
