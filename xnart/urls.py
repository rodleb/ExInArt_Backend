"""xnart URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.schemas import get_schema_view
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
# from .views import protected_view
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token
from django.conf.urls import url
from rest_framework_swagger.views import get_swagger_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView





from drf_yasg import openapi
schema_view = get_schema_view(
    openapi.Info(
        title="ExInARt API",
        default_version='v1',
        description="Your API description",
        terms_of_service="https://www.yourapp.com/terms/",
        contact=openapi.Contact(email="contact@yourapp.com"),
        license=openapi.License(name="Your License"),

    ),
    public=True,
    permission_classes=[AllowAny] 
    
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('users_api.urls')),  # Include your users_api app's URLs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('network/', include('user_network_api.urls')),  # Include your user_network_api app's URLs
    #JWT token refresh and shit
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # url(r'^api-token-verify/', verify_jwt_token),
]