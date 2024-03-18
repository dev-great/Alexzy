from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.staticfiles.urls import static

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Alexzy API Documentation",
        default_version='v1',
        description="Alexzy is a powerful e-commerce platform designed for businesses sales.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="hello@Alexzy.app"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/authentication/',
         include('authentication.urls', namespace='authentication')),
    path('api/v1/products/', include('products.urls', namespace='products')),
    path('api/v1/blog/', include('blog.urls', namespace='blog')),
    path('api/v1/payment/', include('payment.urls', namespace='payment')),
    path('api/v1/order/', include('order.urls', namespace='order')),
    path('api/v1/symbiosis/', include('symbiosis.urls', namespace='symbiosis')),
    # Documentation
    path('api/v1/docs/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = 'Alexzy Control Panel'
admin.site.index_title = 'Administrators Dashboard'
admin.site.site_title = 'Control Panel'
