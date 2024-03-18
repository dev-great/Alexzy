from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
User = get_user_model()


class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage
        fields = ['id', 'image',]


# class ProductBrandSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductTag
#         fields = ['tag',]


class ProductBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBrand
        fields = '__all__'


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'


class ProductColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductColor
        fields = '__all__'


class FilterNameSerializer(serializers.RelatedField):
    def to_representation(self, value):
        return value.name if value else None


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    color = ProductColorSerializer(many=True, read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(read_only=True)
    filter_by = FilterNameSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class WishlistSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Wishlist
        fields = '__all__'


class BestSellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = BestSeller
        fields = '__all__'


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = '__all__'
