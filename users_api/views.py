# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpRequest  # Import HttpRequest
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, UserProfileUpdateSerializer, PublicUserProfileSerializer, UpdateProfilePictureSerializer, PrivateUserProfileSerializer, ForgotPasswordSerializer, ChangePasswordSerializer
import secrets
import datetime
from .models import CustomUser as User  # Import your User model
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import parser_classes
import os
import uuid
from firebase_admin import storage
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from xnart.user_permissions import IsVerifiedUser
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
import random
import string
import os
import uuid
import datetime
from firebase_admin import storage
from rest_framework import status
from rest_framework.response import Response
from rest_framework import status
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated






#Fixed and Ready to go

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'email': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
            'confirm_password': openapi.Schema(type=openapi.TYPE_STRING),
            'first_name': openapi.Schema(type=openapi.TYPE_STRING),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={200: 'Successful login'}
)
@api_view(['POST'])
@authentication_classes([])  # No authentication required
@permission_classes([])  # No permission required
def register_user(request):
    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # Save the user instance returned by the serializer's create method

            # Generate access and refresh tokens
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token

            # Generate the verification link
            verification_link = generate_verification_link(request, user)

            
            user_email = user.email
            first_name = user.first_name
            last_name = user.last_name
            user_id = user.id
            username = user.username

            response_data = {
                'message': 'User created successfully.',
                'access_token': str(access),
                'refresh_token': str(refresh),
                'verification_link': verification_link,
                'user_email': user_email,
                'first_name': first_name,
                'last_name': last_name,
                'user_id': user_id,
                'username': username,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@swagger_auto_schema(
    method='POST',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={200: 'Successful login'}
)
@api_view(['POST'])
@authentication_classes([])  # No authentication required
@permission_classes([])  # No permission required
def user_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if username and password:
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_active:
                return Response({"message": "User account is not active."}, status=400)

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            user.last_login = timezone.now()
            user.save()

            user_email = user.email
            first_name = user.first_name
            last_name = user.last_name
            user_id = user.id
            username = user.username
            profile_picture = user.profile_picture
            is_verified = user.is_verified
            
            ##if user is verified then return true else return verification link and false
            if is_verified:
                response_data = {
                "message": "You have successfully logged in.",
                "access_token": access_token,
                "refresh_token": str(refresh),
                "user_email": user_email,
                "first_name": first_name,
                "last_name": last_name,
                "user_id": user_id,
                "username": username,
                "profile_picture": profile_picture,
                "is_verified": is_verified,
                }
            else:
                verification_link = generate_verification_link(request, user)
                response_data = {
                "message": "You have successfully logged in.",
                "access_token": access_token,
                "refresh_token": str(refresh),
                "user_email": user_email,
                "first_name": first_name,
                "last_name": last_name,
                "user_id": user_id,
                "username": username,
                "profile_picture": profile_picture,
                "is_verified": is_verified,
                "verification_link": verification_link,
                }

            return Response(response_data)
        else:
            return Response({"message": "Unable to log in with provided credentials."}, status=400)
    else:
        return Response({"message": "Must include 'username' and 'password' fields."}, status=400)


@swagger_auto_schema(
    method='put',
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
            description='Bearer <access_token>'
        )
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
          #        fields = [ 'first_name', 'last_name', 'biography', 'profile_picture']
            'first_name': openapi.Schema(type=openapi.TYPE_STRING),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING),
            'biography': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={200: 'Successful login'}
)
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_user_profile(request, *args, **kwargs):
    user = request.user
    serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    responses={200: 'Private user profile retrieved successfully'}
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_private_user_profile(request, *args, **kwargs):
    # Get the Bearer token from the Authorization header
    authorization_header = request.META.get('HTTP_AUTHORIZATION', '')
    print("Authorization header:", authorization_header)
    
    # Extract the token from the header
    if authorization_header.startswith('Bearer '):
        token = authorization_header.split()[1]
        print("Received token:", token)
    else:
        print("No Bearer token found")

    user = request.user
    serializer = PrivateUserProfileSerializer(user)
    return Response(serializer.data)


## Fixed for FireBase storage
@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
            description='Bearer <access_token>'
        )
    ],
    consumes=['multipart/form-data'],
    responses={200: 'Profile picture updated successfully'}
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsVerifiedUser])
@parser_classes([MultiPartParser])
def update_profile_picture(request):
    if request.method == 'POST':
        serializer = UpdateProfilePictureSerializer(request.user, data=request.data)
        if serializer.is_valid():
            image_file = request.FILES.get('profile_picture')

            # Generate a unique filename using UUID
            new_filename = f"{uuid.uuid4()}{os.path.splitext(image_file.name)[-1]}"

            # Initialize Firebase Admin SDK (assuming you've already initialized it)
            # and get a reference to the default Firebase Storage bucket
            bucket = storage.bucket('exinart-13556.appspot.com')  # This will use the default bucket configured in Firebase Admin

            # Upload the image to Firebase Storage
            blob = bucket.blob(f"profile_pictures/{new_filename}")
            blob.upload_from_string(image_file.read(), content_type=image_file.content_type)
            
            expiration = datetime.timedelta(days=7)
            print("Expiration:", expiration)

            # Get the Direct Google Cloud Storage URL
            direct_url = blob.generate_signed_url(
                version="v4",
                expiration=expiration,
                method="GET",
            )

            # Update the profile picture URL in the serializer
            serializer.validated_data['profile_picture'] = direct_url
            serializer.save()

            return Response({'message': 'Profile picture updated successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            name='username',
            in_=openapi.IN_PATH,
            type=openapi.TYPE_STRING,
            required=True,
            description='Username of the user'
        )
    ],
    responses={200: 'Public user profile retrieved successfully', 404: 'User not found'}
)
@api_view(['GET'])
@authentication_classes([])  # No authentication required
@permission_classes([])  # No permission required
def get_public_user_profile(request, username):
    try:
        user = User.objects.get(username=username)
        serializer = PublicUserProfileSerializer(user)
        return Response(serializer.data)
    except Exception as e:
        return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)



@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            name='token',
            in_=openapi.IN_PATH,
            type=openapi.TYPE_STRING,
            required=True,
            description='Verification token received in email'
        )
    ],
    responses={200: 'Account verified successfully', 400: 'Invalid verification token'}
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def verify_account(request, token):

    #if token is already verified to a user then return message that user is already verified
    try:
        user = User.objects.get(verification_token=token)
        if user.is_verified:
            return Response({'message': 'User is already verified.'}, status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist:
        return Response({'message': 'Invalid verification token.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if token:
        try:
            # Get user with the verification token
            user = User.objects.get(verification_token=token)
            user.is_verified = True
            user.save()

            return Response({'message': 'Your account has been verified successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Invalid verification token.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'message': 'Verification token not provided.'}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
     manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
            description='Bearer Token'
        )
    ],
    responses={200: 'Resend verification code successful'}
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])  # Require JWT authentication for the view
@permission_classes([IsAuthenticated])  # Allow only authenticated users
def resend_verification_code(request):
    # Get the user's email from the authenticated JWT token payload
    user_email = request.user.email

    try:
        user = User.objects.get(email=user_email)
    except User.DoesNotExist:
        return Response({'error': 'User not found with the provided email.'}, status=status.HTTP_404_NOT_FOUND)

    verification_link = generate_verification_link(request, user)

    return Response({'message': 'Verification link sent successfully.',
                     'verification_link': str(verification_link)
                     }, status=status.HTTP_200_OK)


#need to be tested

#logout user
@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={200: 'Successful logout', 400: 'Bad Request'}
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def user_logout(request):
    try:
        refresh_token = request.data['refresh_token']
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'You have been logged out successfully.'}, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({'error': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)

    

#forget password

@swagger_auto_schema(
        
    method='post',

    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={200: 'Successful login'}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    serializer = ForgotPasswordSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'User not found with the provided email.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Generate a random password reset token
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        user.password_reset_token = token
        user.save()

        # Send password reset link to the user's email
        subject = 'Password Reset'
        message = f'Click the following link to reset your password: http://example.com/reset-password/?token={token}'
        from_email = 'noreply@example.com'
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)

        return Response({'message': 'Password reset link sent to your email.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#change password
@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'old_password': openapi.Schema(type=openapi.TYPE_STRING),
            'new_password': openapi.Schema(type=openapi.TYPE_STRING),
            'confirm_new_password': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={200: 'Password changed successfully', 400: 'Bad Request'}
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data, context={'user': request.user})
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

## Helper functions
def generate_verification_link(request, user):
    # Generate a verification token using the user's email and a secret key
    verification_token = secrets.token_urlsafe(16)

    # Set the verification token for the user
    user.verification_token = verification_token
    user.save()

    # Generate the verification link
    verification_url = reverse('verify-code', args=[verification_token])
    verification_link = request.build_absolute_uri(verification_url)

    return verification_link



