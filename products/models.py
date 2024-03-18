import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from cloudinary.models import CloudinaryField

User = get_user_model()


def get_product_image_upload_path(instance, filename):
    folder_path = f"product/user_shop/{instance.product_id}/{timezone.now().strftime('%Y/%m/%d')}/"
    return folder_path + filename


def get_brand_image_upload_path(instance, filename):
    folder_path = f"product/user_shop/{timezone.now().strftime('%Y/%m/%d')}/"
    return folder_path + filename

# class ProductTag(models.Model):
#     id = models.UUIDField(
#         primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
#     tag = models.CharField(max_length=1000)
#     created_on = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return str(self.tag)

#     class Meta:
#         ordering = ['-created_on']


class ProductBrand(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    brand = models.CharField(max_length=1000)
    image = CloudinaryField('image', transformation={'width': 2000, 'height': 2000, 'crop': 'fill'})
    content = models.TextField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.brand)

    class Meta:
        ordering = ['-created_on']


class ProductCategory(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    category = models.CharField(max_length=200)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.category)

    class Meta:
        ordering = ['-created_on']


class ProductColor(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    color = models.CharField(max_length=200)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.color)

    class Meta:
        ordering = ['-created_on']


class Filter(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('Used / Preowned', 'Used / Preowned'),
    ]
    TYPE_CHOICES = [
        ('yes', 'yes'),
        ('no', 'no'),
    ]
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=1000)
    brand = models.ForeignKey(
        ProductBrand, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(
        ProductCategory, on_delete=models.CASCADE, null=True, blank=True)
    color = models.ManyToManyField(ProductColor)
    quantity = models.IntegerField()
    filter_by = models.ManyToManyField(Filter)
    description = models.TextField(db_index=True, null=True, blank=True)
    price = models.DecimalField(
        default=0, max_digits=10, decimal_places=2)
    commission = models.DecimalField(
        default=0, max_digits=10, decimal_places=2,)
    youtube = models.TextField(db_index=True, null=True, blank=True)
    ram = models.IntegerField(null=True, blank=True)
    storage = models.CharField(max_length=200, null=True, blank=True)
    processor = models.CharField(max_length=200, null=True, blank=True)
    screen_size = models.CharField(max_length=200, null=True, blank=True)
    touch_screen = models.CharField(
        max_length=5, choices=TYPE_CHOICES, default='no')
    backlight_keyboard = models.CharField(
        max_length=5, choices=TYPE_CHOICES, default='no')
    convertible = models.CharField(
        max_length=5, choices=TYPE_CHOICES, default='no')
    webcam = models.CharField(
        max_length=5, choices=TYPE_CHOICES, default='no')
    dedicated_video_ram = models.CharField(
        max_length=200, null=True, blank=True)
    graphics_card = models.CharField(max_length=200, null=True, blank=True)
    condition = models.CharField(max_length=200, null=True, blank=True)
    package_include = models.TextField(db_index=True, null=True, blank=True)
    battery_life = models.CharField(max_length=200, null=True, blank=True)
    condition = models.CharField(
        max_length=15, choices=CONDITION_CHOICES, default='new')
    online_presence = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)

    # Add more fields as per your requirements
    def __str__(self):
        return self.product_name

    class Meta:
        ordering = ['-created_on']

    # Format the money count with comma as thousand separator
    def formatted_product_price(self):
        return "{:,.2f}".format(self.product_price)


class BestSeller(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Testimonial(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    product_id = models.ForeignKey(
        Product, on_delete=models.CASCADE)
    image = CloudinaryField('image', transformation={
                            'width': 300, 'height': 300, 'crop': 'fill'})
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_on']


class Wishlist(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, related_name='wishlists')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
