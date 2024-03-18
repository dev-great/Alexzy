from django.urls import path
from .views import *

app_name = 'products'

urlpatterns = [
    path('all_products/', GetAllProductView.as_view()),
    path('categories/', CategoryView.as_view(), name='categories'),
    path('testimonial/', GetTestimonialView.as_view(), name='testimonial'),
    path('best_seller/', GetBestSellerView.as_view(), name='best_seller'),
    path('brands/', BrandView.as_view(), name='brands'),
    path('wishlist/', WishlistAPIView.as_view(), name='wishlist-list'),
    path('generate_link/', GenerateProductByIDLinkView.as_view(),
         name='generate_link_id'),
    path('', GetProductByIDView.as_view(),
         name='get-product-by-id'),
]
