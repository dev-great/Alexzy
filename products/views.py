
from authentication.models import ReferralCode
from common.custom_pagination import CustomPagination
from common.unique_reponse import process_data
from .serializer import *
from .models import *
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError

User = get_user_model()


# Create your views here.


class CustomValidationException(Exception):
    def __init__(self, error, message, status_code=status.HTTP_400_BAD_REQUEST, *args, **kwargs):
        self.error = error,
        self.message = message,
        self.status_code = status_code
        super().__init__(*args, **kwargs)


class GetProductByIDView(APIView):

    @swagger_auto_schema(responses={200: ProductSerializer()})
    def get(self, request):
        try:
            pk = request.query_params.get('pk')

            if not pk:
                return Response({
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "message": "Missing 'pk' query parameter in the request.",
                }, status=status.HTTP_400_BAD_REQUEST)

            product = Product.objects.get(id=pk)
            product_images = ProductImage.objects.filter(
                product_id=pk)

            product_serializer = ProductSerializer(product)
            image_serializer = ProductImageSerializer(
                product_images, many=True)
            product_data = product_serializer.data
            image_data = image_serializer.data
            for image in image_data:
                image_id = image['id']
                image['image'] = f"{image['image']}?id={image_id}"
            product_data['images'] = image_data
            product_data["brand"] = ProductBrand.objects.get(
                id=product_data["brand"]).brand
            product_data["category"] = ProductCategory.objects.get(
                id=product_data["category"]).category
            return Response({
                "statusCode": status.HTTP_200_OK,
                "message": "Successfully.",
                "data": product_data,
            }, status=status.HTTP_200_OK)

        except Product.DoesNotExist:
            return Response({
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "Product not found.",
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Server error",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetTestimonialView(APIView):

    @swagger_auto_schema(responses={200: TestimonialSerializer()})
    def get(self, request):
        try:
            testimonial = Testimonial.objects.all()

            serializer = TestimonialSerializer(testimonial, many=True)

            return Response({
                "statusCode": status.HTTP_200_OK,
                "message": "Successfully.",
                "data": serializer.data,
            }, status=status.HTTP_200_OK)

        except Product.DoesNotExist:
            return Response({
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "Testimonial not found.",
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Server error",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetBestSellerView(APIView):

    @swagger_auto_schema(responses={200: BestSellerSerializer()})
    def get(self, request):
        try:
            best_seller = BestSeller.objects.first()

            if best_seller:
                # Retrieve associated product and images
                product = best_seller.product_id
                product_serializer = ProductSerializer(product)
                product_images = ProductImage.objects.filter(
                    product_id=product)
                image_serializer = ProductImageSerializer(
                    product_images, many=True)

                # Add product and image data to the BestSeller serializer data
                best_seller_data = BestSellerSerializer(best_seller).data
                best_seller_data['product'] = product_serializer.data
                best_seller_data['product_images'] = image_serializer.data

                return Response({
                    "statusCode": status.HTTP_200_OK,
                    "message": "Successfully.",
                    "data": best_seller_data,
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "statusCode": status.HTTP_404_NOT_FOUND,
                    "message": "BestSeller not found.",
                }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Server error",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetAllProductView(APIView, CustomPagination):
    pagination_class = CustomPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('product_name', openapi.IN_QUERY,
                              description="Product name to search for.", type=openapi.TYPE_STRING),
            openapi.Parameter('description', openapi.IN_QUERY,
                              description="Description of the product to search for.", type=openapi.TYPE_STRING),
            openapi.Parameter('category', openapi.IN_QUERY,
                              description="Category of the product to filter by.", type=openapi.TYPE_STRING),

            openapi.Parameter('ram', openapi.IN_QUERY,
                              description="ram to filter by.", type=openapi.TYPE_STRING),

            openapi.Parameter('storage', openapi.IN_QUERY,
                              description="storage to filter by.", type=openapi.TYPE_STRING),

            openapi.Parameter('processor', openapi.IN_QUERY,
                              description="processor name to filter by.", type=openapi.TYPE_STRING),

            openapi.Parameter('brand', openapi.IN_QUERY,
                              description="Brand name to filter by.", type=openapi.TYPE_STRING),

            openapi.Parameter('sort_by_price', openapi.IN_QUERY,
                              description="sort_by_price to filter by.", type=openapi.TYPE_STRING),

            openapi.Parameter('min_price', openapi.IN_QUERY,
                              description="min_price to filter by.", type=openapi.TYPE_STRING),

            openapi.Parameter('max_price', openapi.IN_QUERY,
                              description="max_price to filter by.", type=openapi.TYPE_STRING),


        ]
    )
    def get(self, request):
        try:
            product_name = request.query_params.get('product_name', '')
            description = request.query_params.get('description', '')
            ram = request.query_params.get('ram', '')
            storage = request.query_params.get('storage', '')
            processor = request.query_params.get('processor', '')
            category_name = request.query_params.get('category', '')
            brand = request.query_params.get('brand', '')
            min_price = request.query_params.get('min_price', 0)
            max_price = request.query_params.get('max_price', 99999999)
            sort_by_price = request.query_params.get('sort_by_price', 'asc')

            # Start with a base queryset
            products = Product.objects.filter(online_presence=True, quantity__gt=0)

            # Apply filters based on query parameters
            if product_name:
                products = products.filter(product_name__icontains=product_name)
            if description:
                products = products.filter(description__icontains=description)
            if ram:
                products = products.filter(ram__icontains=ram)
            if storage:
                products = products.filter(storage__icontains=storage)
            if processor:
                products = products.filter(processor__icontains=processor)
            if category_name:
                products = products.filter(category__category=category_name)
            if brand:
                products = products.filter(brand__brand=brand)
            if min_price is not None and max_price is not None:
                if sort_by_price == 'asc':
                    products = products.filter(price__gte=min_price, price__lte=max_price).order_by('price')
                elif sort_by_price == 'desc':
                    products = products.filter(price__gte=min_price, price__lte=max_price).order_by('-price')

            # Paginate the queryset
            paginated_products = self.paginate_queryset(products, request)
            serializer = ProductSerializer(paginated_products, many=True)
            serialized_data = serializer.data

            # Fetch brand and category names separately
            brand = {brand.id: brand.brand for brand in ProductBrand.objects.all()}
            category_names = {category.id: category.category for category in ProductCategory.objects.all()}

            # Append image data to each product
            for product_data in serialized_data:
                product_id = product_data['id']
                product_data['brand'] = brand.get(product_data['brand'])
                product_data['category'] = category_names.get(product_data['category'])
                product_images = ProductImage.objects.filter(product_id=product_id)
                image_serializer = ProductImageSerializer(product_images, many=True)
                image_data = [{'image': f"{image['image']}"} for image in image_serializer.data]
                product_data['images'] = image_data

            return self.get_paginated_response(serialized_data)
        except Exception as e:
            return Response({
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Server error",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BrandView(APIView):

    def get(self, request):
        try:
            brand = ProductBrand.objects.all()
            processed_data = ProductBrandSerializer(brand, many=True)
            return Response({
                "statusCode": status.HTTP_200_OK,
                "message": "Successfully retrieved viewed products.",
                "data": processed_data.data,
            })
        except Exception as e:
            return Response({
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Server error",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CategoryView(APIView):

    def get(self, request):
        try:
            category_names = ProductCategory.objects.all()
            processed_data = ProductCategorySerializer(
                category_names, many=True)
            return Response({
                "statusCode": status.HTTP_200_OK,
                "message": "Successfully retrieved viewed products.",
                "data": processed_data.data,
            })
        except Exception as e:
            return Response({
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Server error",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WishlistAPIView(APIView, CustomPagination):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        try:
            user_email = request.user.email
            print(user_email)
            wishlists = Wishlist.objects.filter(user__email=user_email)
            print(wishlists)

            # Check if there are no wishlists
            if not wishlists:
                raise ObjectDoesNotExist("No wishlists found for this user.")

            response_data = []
            paginated_wishlists = self.paginate_queryset(wishlists, request)

            # Create a set to store unique product IDs
            unique_product_ids = set()

            for wishlist in paginated_wishlists:
                product_ids = wishlist.products.all()

                for product in product_ids:

                    product_id = product.id
                    if product_id not in unique_product_ids:
                        product_serializer = ProductSerializer(product)
                        product_data = product_serializer.data

                        product_data["wishlist_id"] = wishlist.id
                        product_data['brand'] = product.brand.brand
                        product_images = ProductImage.objects.filter(
                            product_id=product)
                        image_serializer = ProductImageSerializer(
                            product_images, many=True)
                        image_data = [{'image': f"{image['image']}.jpg"}
                                      for image in image_serializer.data]
                        product_data['images'] = image_data
                        product_data['store_id'] = product.store_id.business_name
                        product_data['category'] = product.category.category
                        print(product_data)
                        response_data.append(product_data)

                        # Add this product ID to the set
                        unique_product_ids.add(product_id)

            payload = {
                "statusCode": status.HTTP_200_OK,
                "message": "Successfully.",
                "data": response_data,
            }

            return self.get_paginated_response(payload)

        except ObjectDoesNotExist as e:
            return Response({
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "No wishlists found.",
                "error": str(e),
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Server error",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        try:
            id = request.data.get('id')
            wishlist_item = Wishlist.objects.get(id=id)
            if wishlist_item.user != request.user:
                return Response({
                    "statusCode": status.HTTP_403_FORBIDDEN,
                    "message": "Permission denied.",
                }, status=status.HTTP_403_FORBIDDEN)

            # Delete the wishlist item
            wishlist_item.delete()

            return Response({
                "statusCode": status.HTTP_204_NO_CONTENT,
                "message": "Wishlist item deleted successfully.",
            }, status=status.HTTP_204_NO_CONTENT)

        except Wishlist.DoesNotExist:
            return Response({
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "Wishlist item not found.",
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Server error",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(request_body=WishlistSerializer)
    def post(self, request):
        try:
            product_id = request.data.get('product_id')
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({
                    "statusCode": status.HTTP_404_NOT_FOUND,
                    "message": "Data error",
                    "error": "Product not found."
                }, status=status.HTTP_404_NOT_FOUND)
            wishlist = Wishlist.objects.create(user=request.user)
            wishlist.products.add(product)
            serializer = WishlistSerializer(wishlist)

            return Response({
                "statusCode": status.HTTP_201_CREATED,
                "message": "Successfully added to wishlist.",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "message": "Validation error",
                "error": str(e),
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Server error",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerateProductByIDLinkView(APIView):

    @swagger_auto_schema(responses={200: ProductSerializer()})
    def get(self, request):
        try:
            referal_user = request.user
            pk = request.query_params.get('pk')

            if not pk:
                return Response({
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "message": "Missing 'pk' query parameter in the request.",
                }, status=status.HTTP_400_BAD_REQUEST)
            try:
                referral_code_object = ReferralCode.objects.get(
                    user=referal_user)
                code = referral_code_object.code
            except ReferralCode.DoesNotExist:
                code = None
            product = Product.objects.get(id=pk)
            product_images = ProductImage.objects.filter(
                product_id=pk)

            product_serializer = ProductSerializer(product)
            image_serializer = ProductImageSerializer(
                product_images, many=True)
            product_data = product_serializer.data
            image_data = image_serializer.data
            for image in image_data:
                image_id = image['id']
                image['image'] = f"{image['image']}?id={image_id}"
            product_data['images'] = image_data
            product_data["brand"] = ProductBrand.objects.get(
                id=product_data["brand"]).brand
            product_data["category"] = ProductCategory.objects.get(
                id=product_data["category"]).category
            return Response({
                "statusCode": status.HTTP_200_OK,
                "message": "Successfully.",
                "referal_code": code,
                "data": product_data,
            }, status=status.HTTP_200_OK)

        except Product.DoesNotExist:
            return Response({
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "Product not found.",
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Server error",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
