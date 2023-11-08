import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


def get_product_image_upload_path(instance, filename):
    folder_path = f"product/user_shop/{instance.product_id}/{timezone.now().strftime('%Y/%m/%d')}/"
    return folder_path + filename


class ProductTag(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    tag = models.CharField(max_length=1000)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-created_on']


class ProductBrand(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    brand = models.CharField(max_length=1000)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-created_on']


class ProductCategory(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    category = models.CharField(max_length=200)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-created_on']


class ProductColor(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    color = models.CharField(max_length=200)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-created_on']


class Filter(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=1000)
    tag = models.ForeignKey(
        ProductTag, on_delete=models.CASCADE, null=True, blank=True)
    brand = models.ForeignKey(
        ProductBrand, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(
        ProductCategory, on_delete=models.CASCADE, null=True, blank=True)
    color = models.ManyToManyField(ProductColor)
    ram = models.IntegerField()
    storage = models.CharField(max_length=200)
    processor = models.CharField(max_length=200)
    filter_by = models.ManyToManyField(Filter)
    description = models.TextField(db_index=True)
    low_product_alert = models.BooleanField(default=False)
    price = models.DecimalField(
        default=0, max_digits=10, decimal_places=2)
    commission = models.DecimalField(
        default=0, max_digits=10, decimal_places=2)
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


class ProductImage(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    product_id = models.ForeignKey(
        Product, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to=get_product_image_upload_path, null=True, blank=True)
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
