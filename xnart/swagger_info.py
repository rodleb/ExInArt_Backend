from drf_yasg import openapi
from rest_framework.permissions import AllowAny


swagger_info = openapi.Info(
    title="Your API Title",
    default_version='v1',
    description="Description of your API",
    terms_of_service="https://www.example.com/terms/",
    contact=openapi.Contact(email="contact@example.com"),
    license=openapi.License(name="Your License"),
    public=True,
    permission_classes=[AllowAny] 
)
