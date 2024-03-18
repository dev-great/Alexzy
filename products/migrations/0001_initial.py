# Generated by Django 3.2 on 2024-03-18 00:42

import cloudinary.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Filter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('product_name', models.CharField(max_length=1000)),
                ('quantity', models.IntegerField()),
                ('description', models.TextField(blank=True, db_index=True, null=True)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('commission', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('youtube', models.TextField(blank=True, db_index=True, null=True)),
                ('ram', models.IntegerField(blank=True, null=True)),
                ('storage', models.CharField(blank=True, max_length=200, null=True)),
                ('processor', models.CharField(blank=True, max_length=200, null=True)),
                ('screen_size', models.CharField(blank=True, max_length=200, null=True)),
                ('touch_screen', models.CharField(choices=[('yes', 'yes'), ('no', 'no')], default='no', max_length=5)),
                ('backlight_keyboard', models.CharField(choices=[('yes', 'yes'), ('no', 'no')], default='no', max_length=5)),
                ('convertible', models.CharField(choices=[('yes', 'yes'), ('no', 'no')], default='no', max_length=5)),
                ('webcam', models.CharField(choices=[('yes', 'yes'), ('no', 'no')], default='no', max_length=5)),
                ('dedicated_video_ram', models.CharField(blank=True, max_length=200, null=True)),
                ('graphics_card', models.CharField(blank=True, max_length=200, null=True)),
                ('package_include', models.TextField(blank=True, db_index=True, null=True)),
                ('battery_life', models.CharField(blank=True, max_length=200, null=True)),
                ('condition', models.CharField(choices=[('new', 'New'), ('Used / Preowned', 'Used / Preowned')], default='new', max_length=15)),
                ('online_presence', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_on'],
            },
        ),
        migrations.CreateModel(
            name='ProductBrand',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('brand', models.CharField(max_length=1000)),
                ('image', cloudinary.models.CloudinaryField(max_length=255, verbose_name='image')),
                ('content', models.TextField(blank=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_on'],
            },
        ),
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('category', models.CharField(max_length=200)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_on'],
            },
        ),
        migrations.CreateModel(
            name='ProductColor',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('color', models.CharField(max_length=200)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_on'],
            },
        ),
        migrations.CreateModel(
            name='Testimonial',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('products', models.ManyToManyField(related_name='wishlists', to='products.Product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('image', cloudinary.models.CloudinaryField(max_length=255, verbose_name='image')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product')),
            ],
            options={
                'ordering': ['-created_on'],
            },
        ),
        migrations.AddField(
            model_name='product',
            name='brand',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.productbrand'),
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.productcategory'),
        ),
        migrations.AddField(
            model_name='product',
            name='color',
            field=models.ManyToManyField(to='products.ProductColor'),
        ),
        migrations.AddField(
            model_name='product',
            name='filter_by',
            field=models.ManyToManyField(to='products.Filter'),
        ),
        migrations.AddField(
            model_name='product',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='BestSeller',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product')),
            ],
        ),
    ]
