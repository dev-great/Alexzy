from common.custom_pagination import CustomPagination
from products.models import ProductBrand, ProductCategory, ProductImage
from products.serializer import ProductImageSerializer, ProductSerializer
from .models import *
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import CartItemSerializer, CartSerializer
from rest_framework.generics import RetrieveAPIView, CreateAPIView
from django.shortcuts import get_object_or_404
from rest_framework import permissions

from drf_yasg.utils import swagger_auto_schema


class CustomValidationException(Exception):
    def __init__(self, error, message, status_code=status.HTTP_400_BAD_REQUEST, *args, **kwargs):
        self.error = error,
        self.message = message,
        self.status_code = status_code
        super().__init__(*args, **kwargs)


class CartAPIView(RetrieveAPIView, CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartSerializer

    def get_object(self):
        user = self.request.user
        cart = Cart.objects.select_related('user').filter(user=user).first()
        if cart:
            return cart
        else:
            return Response({
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "Data error.",
                "error": "Cart not found.",
            }, status=status.HTTP_404_NOT_FOUND
            )

    def retrieve(self, request, *args, **kwargs):
        try:
            cart = self.get_object()
            serializer = self.get_serializer(cart)
            return Response({
                "statusCode": status.HTTP_200_OK,
                "message": "Successfully.",
                "data": serializer.data,
            }, status=status.HTTP_200_OK)
        except Cart.DoesNotExist as e:
            return Response({
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Server error",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(request_body=CartSerializer)
    def create(self, request, *args, **kwargs):
        try:
            cart = self.get_object()
            return Response({
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "Data error.",
                "error": "A cart already exists for this user.",
            }, status=status.HTTP_404_NOT_FOUND
            )
        except Cart.DoesNotExist:
            user = request.user
            cart = Cart.objects.create(user=user)
            serializer = self.get_serializer(cart)
            return Response({
                "statusCode": status.HTTP_201_CREATED,
                "message": "Successfully.",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)


class CartItemsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        cart_items = CartItem.objects.filter(
            cart__user=user).select_related('product')
        serializer = CartItemSerializer(cart_items, many=True)

        cart_items_data = []
        for cart_item in cart_items:
            product = cart_item.product
            product_images = ProductImage.objects.filter(product_id=product.id)
            user_phone_number = product.user_id.phone_number
            user_id = product.user_id.id
            print(user_phone_number)
            product_serializer = ProductSerializer(product)
            image_serializer = ProductImageSerializer(
                product_images, many=True)
            product_data = product_serializer.data
            image_data = image_serializer.data
            image_data = [{'image': f"{image['image']}.jpg"}
                          for image in image_data]
            product_data['images'] = image_data

            product_data["brand"] = ProductBrand.objects.get(
                id=product_data["brand"]).brand_name
            product_data["category"] = ProductCategory.objects.get(
                id=product_data["category"]).category

            cart_item_serializer = CartItemSerializer(cart_item)
            cart_item_data = cart_item_serializer.data
            cart_item_data['product'] = product_data

            cart_items_data.append({
                'cart_item': cart_item_data,
                "user_id": user_id,
                "user_phone_number": user_phone_number,
            })

        return Response({
            "statusCode": status.HTTP_200_OK,
            "message": "Successfully.",
            "data": cart_items_data,
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=CartItemSerializer)
    def post(self, request):
        user = request.user
        data = request.data
        serializer = CartItemSerializer(data=data)
        cart_items_data = []

        if serializer.is_valid():
            # Retrieve data from the serializer
            cart = serializer.validated_data.get("cart")
            product = serializer.validated_data.get("product")
            quantity = serializer.validated_data.get("quantity")
            price = serializer.validated_data.get("price")
            # Check if the same product with the same variation already exists in the cart
            existing_cart_item = CartItem.objects.filter(
                cart=cart, product=product).first()

            if existing_cart_item:
                # If it exists, update the quantity and other details
                existing_cart_item.quantity += quantity
                existing_cart_item.price = price
                existing_cart_item.save()
                cart_item_serializer = CartItemSerializer(existing_cart_item)
            else:
                # If it doesn't exist, create a new cart item
                cart_item = CartItem.objects.create(
                    cart=cart,
                    product=product,
                    quantity=quantity,
                    price=price,
                )
                cart_item_serializer = CartItemSerializer(cart_item)

            # Retrieve product and related data
            product_images = ProductImage.objects.filter(product_id=product.id)
            product_serializer = ProductSerializer(product)
            image_serializer = ProductImageSerializer(
                product_images, many=True)
            product_data = product_serializer.data
            image_data = [{'image': f"{image['image']}.jpg"}
                          for image in image_serializer.data]
            product_data['images'] = image_data
            product_data["brand"] = ProductBrand.objects.get(
                id=product_data["brand"]).brand
            product_data["category"] = ProductCategory.objects.get(
                id=product_data["category"]).category

            # Prepare cart item data for response
            cart_item_data = cart_item_serializer.data
            cart_item_data['product'] = product_data

            cart_items_data.append({
                'cart_item': cart_item_data,
            })

            return Response({
                "statusCode": status.HTTP_201_CREATED,
                "message": "Successfully.",
                "data": cart_items_data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "Data error.",
                "error": serializer.errors,
            }, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(responses={200: CartItemSerializer()})
    def patch(self, request):
        pk = request.query_params.get('pk')
        user = request.user
        cart_item = get_object_or_404(CartItem, pk=pk, cart__user=user)
        data = request.data
        serializer = CartItemSerializer(cart_item, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": status.HTTP_201_CREATED,
                "message": "Successfully.",
                "data": CartItemSerializer(cart_item).data,
            }, status=status.HTTP_201_CREATED)

        return Response({
            "statusCode": status.HTTP_404_NOT_FOUND,
            "message": "Data error.",
            "error": serializer.errors,
        }, status=status.HTTP_404_NOT_FOUND
        )

    def delete(self, request):

        pk = request.query_params.get('pk')
        user = request.user
        cart_item = get_object_or_404(CartItem, pk=pk, cart__user=user)

        cart_item.delete()

        return Response({
            "statusCode": status.HTTP_204_NO_CONTENT,
            "message": "Cart item deleted successfully.",
        }, status=status.HTTP_204_NO_CONTENT)
