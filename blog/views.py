from rest_framework import generics, filters, viewsets
from rest_framework.generics import ListAPIView
from common.custom_pagination import CustomPagination
from .serializer import *
from .models import *
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics


class CustomValidationException(Exception):
    def __init__(self, error, message, status_code=status.HTTP_400_BAD_REQUEST, *args, **kwargs):
        self.error = error,
        self.message = message,
        self.status_code = status_code
        super().__init__(*args, **kwargs)


class ArticleList(ListAPIView):
    def get(self, request, format=None):
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)


class AuthorDetail(APIView):
    def get(self, request, pk):
        try:
            author = Author.objects.get(pk=pk)
            serializer = AuthorSerializer(author)
            payload = {
                "statusCode": status.HTTP_200_OK,
                "message": "Successfully.",
                "data": serializer.data,
            },
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({
                "status": "Not Found",
                "message": "Author not found.",
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "status": "Internal Server Error",
                "message": "An error occurred while processing your request.",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CategoryList(APIView):
    def get(self, request):
        try:
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)

            return Response({
                "statusCode": status.HTTP_200_OK,
                "message": "Successfully.",
                "data": serializer.data,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "Internal Server Error",
                "message": "An error occurred while processing your request.",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ArticleList(APIView):

    def get(self, request):
        try:
            queryset = Article.objects.all()

            # Filtering based on query parameters
            category_id = request.query_params.get('category_id')
            if category_id:
                queryset = queryset.filter(category_id=category_id)

            # Search functionality
            search_query = request.query_params.get('search', '')
            if search_query:
                queryset = queryset.filter(
                    Q(title__icontains=search_query) | Q(content__icontains=search_query))

            serializer = ArticleSerializer(queryset, many=True)

            return Response({
                "statusCode": status.HTTP_200_OK,
                "message": "Successfully.",
                "data": serializer.data,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "Internal Server Error",
                "message": "An error occurred while processing your request.",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommentList(APIView):

    def get(self, request):
        try:
            queryset = Comment.objects.all()
            serializer = CommentSerializer(queryset, many=True)

            return Response({
                "statusCode": status.HTTP_200_OK,
                "message": "Successfully.",
                "data": serializer.data,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "Internal Server Error",
                "message": "An error occurred while processing your request.",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = CommentSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()

                return Response({
                    "statusCode": status.HTTP_201_CREATED,
                    "message": "Successfully.",
                    "data": serializer.data,
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "message": "Data error.",
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "status": "Internal Server Error",
                "message": "An error occurred while processing your request.",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ImageViewSet(APIView):

    def get(self, request):
        try:
            queryset = Image.objects.all()
            serializer = ImageSerializer(queryset, many=True)

            return Response({
                "statusCode": status.HTTP_200_OK,
                "message": "Successfully.",
                "data": serializer.data,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "Internal Server Error",
                "message": "An error occurred while processing your request.",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ArticleDetailView(APIView):
    def get(self, request, pk):
        try:
            article = Article.objects.get(pk=pk)
            serializer = ArticleSerializer(article)
            return Response({
                "statusCode": status.HTTP_200_OK,
                "message": "Successfully.",
                "data": serializer.data,
            }, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({
                "status": "Not Found",
                "message": "Article not found.",
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "status": "Internal Server Error",
                "message": "An error occurred while processing your request.",
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
