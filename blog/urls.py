from django.urls import path
from .views import *

app_name = 'blog'

urlpatterns = [
    path('categories/', CategoryList.as_view(), name='category-list'),
    path('articles/', ArticleList.as_view(), name='article-list'),
    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article-detail'),
    path('comments/', CommentList.as_view(), name='comment-list'),
]
