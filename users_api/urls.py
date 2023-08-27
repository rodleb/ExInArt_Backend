# urls.py
from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView


urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.user_login, name='token_obtain_pair'),
    path('profile/update/', views.update_user_profile, name='update-profile'),
    path('profile/<str:username>/', views.get_public_user_profile, name='get-public-profile'),
    path('profile/<str:username>/private/', views.get_private_user_profile, name='get-private-profile'),
    path('profile/<str:username>/verify/', views.verify_account, name='verify-account'),
    path('update-profile-picture/', views.update_profile_picture, name='update-profile-picture'),
    path('resend-verification-code/', views.resend_verification_code, name='send_verification_code'),
    path('verify-code/<str:token>/', views.verify_account, name='verify-code'),
    path('change-password/', views.change_password, name='change-password'),
    path('logout/', views.user_logout, name='logout'),
    path('forget-password/', views.forgot_password, name='forget-password'),
]