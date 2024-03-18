from common.custom_pagination import CustomPagination
from products.models import ProductImage
from products.serializer import ProductImageSerializer, ProductSerializer
from .models import *
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import OrderItemSerializer, OrderSerializer, ShippingAddressSerializer

from django.shortcuts import get_object_or_404
from rest_framework import permissions
from drf_yasg import openapi
from django.db import transaction

from rest_framework.generics import ListCreateAPIView
from rest_framework.exceptions import NotFound
from drf_yasg.utils import swagger_auto_schema


class CustomValidationException(Exception):
    def __init__(self, error, message, status_code=status.HTTP_400_BAD_REQUEST, *args, **kwargs):
        self.error = error,
        self.message = message,
        self.status_code = status_code
        super().__init__(*args, **kwargs)


class ShippingAddressAPIView(ListCreateAPIView):
    serializer_class = ShippingAddressSerializer

    def get_queryset(self):
        user = self.request.user
        addresses = ShippingAddress.objects.filter(
            user=user).select_related('user')
        return addresses

    def get(self, request, *args, **kwargs):

        addresses = self.get_queryset()
        serializer = self.serializer_class(addresses, many=True)
        return Response({
            "statusCode": status.HTTP_200_OK,
            "message": "Successfully.",
            "data": serializer.data,
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ShippingAddressSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        try:
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response({
                    "statusCode": status.HTTP_201_CREATED,
                    "message": "Successfully.",
                    "data": serializer.data,
                }, status=status.HTTP_201_CREATED)
            return Response({
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "Data error.",
                "error": serializer.errors,
            }, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Server error",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(request_body=ShippingAddressSerializer)
    def patch(self, request, *args, **kwargs):
        try:
            shipping_address = ShippingAddress.objects.get(user=request.user)
            serializer = ShippingAddressSerializer(
                shipping_address, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "statusCode": status.HTTP_200_OK,
                    "message": "Successfully updated.",
                    "data": serializer.data,
                }, status=status.HTTP_200_OK)

            return Response({
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "message": "Data error.",
                "error": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        except ShippingAddress.DoesNotExist:
            raise NotFound("Shipping address not found.")

        except Exception as e:
            return Response({
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Server error",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderAPIView(APIView, CustomPagination):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        page = self.paginate_queryset(orders, request)

        # Serialize the orders
        orders_data = []
        for order in page:
            order_serializer = OrderSerializer(
                order)  # Serialize the current order
            order_data = order_serializer.data
            order_data['order_items'] = []

            order_items = OrderItem.objects.filter(order=order)

            for order_item in order_items:
                order_item_serializer = OrderItemSerializer(order_item)
                order_item_data = order_item_serializer.data

                product = Product.objects.get(id=order_item.product.id)
                product_serializer = ProductSerializer(product)
                order_item_data['product'] = product_serializer.data

                # Fetch and serialize associated product images
                product_images = ProductImage.objects.filter(
                    product_id=order_item.product)
                image_serializer = ProductImageSerializer(
                    product_images, many=True)
                order_item_data['product_images'] = image_serializer.data

                order_data['order_items'].append(order_item_data)

            orders_data.append(order_data)

        return self.get_paginated_response(orders_data)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('order_id', openapi.IN_QUERY,
                              description="Enter the order id.", type=openapi.TYPE_STRING),
        ],
        request_body=OrderSerializer
    )
    def patch(self, request):
        order_id = request.data.get('order_id')
        if order_id is None:
            return Response({
                "message": "order_id is required in the query parameters."
            }, status=status.HTTP_400_BAD_REQUEST)

        order = get_object_or_404(Order, id=order_id)
        serializer = OrderSerializer(order, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "statusCode": status.HTTP_200_OK,
                "message": "Success",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "statusCode": status.HTTP_404_NOT_FOUND,
            "message": "Data error",
            "error": serializer.errors,
        }, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(request_body=OrderSerializer)
    def post(self, request):
        address_id = request.data.get('address_id', None)
        total_price = request.data.get('total_price')
        order_items_data = request.data.get('order_items', [])
        user = request.user

        if address_id is None:
            return Response({
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "message": "Bad Request",
                "error": "Address ID is required in the request body.",
            }, status=status.HTTP_400_BAD_REQUEST)

        shipping_address = get_object_or_404(ShippingAddress, pk=address_id)

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    user=user, status='ORDER PLACED', total_price=total_price, address=shipping_address
                )
                # Iterate through cart items and create order items
                for item_data in order_items_data:
                    product_id = item_data.get("product_id")
                    varient = item_data.get("varient")
                    quantity = item_data.get("quantity")
                    price = item_data.get("price")

                    order_item = OrderItem.objects.create(
                        order=order,
                        product_id=product_id,
                        varient=varient,
                        quantity=quantity,
                        price=price
                    )

        except Exception as e:
            return Response({
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Server error",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = OrderSerializer(order)
        return Response({
            "statusCode": status.HTTP_200_OK,
            "message": "Success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
