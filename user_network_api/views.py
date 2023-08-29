from rest_framework.decorators import api_view, authentication_classes, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Inspiration
from .serializers import InspirationSerializer, PostSerializer
from xnart.user_permissions import IsVerifiedUser
from rest_framework.parsers import MultiPartParser
from google.cloud import storage
import os
import uuid
import datetime 
from users_api.models import CustomUser
from .models import Post
from django.contrib.auth import get_user_model
from .serializers import LikeSerializer, CommentSerializer
from .models import Post, Like, Comment
from rest_framework.pagination import PageNumberPagination





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
    responses={200: 'Successful operation'}
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsVerifiedUser])
def follow_user(request, user_id):
    if user_id == request.user.id:
        return Response({'message': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = InspirationSerializer(data={'followed': user_id}, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'You are now following this user.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    responses={200: 'Successful operation'}
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsVerifiedUser])
def unfollow_user(request, user_id):
    if not Inspiration.objects.filter(follower=request.user, followed_id=user_id).exists():
        return Response({'message': 'You are not following this user.'}, status=status.HTTP_400_BAD_REQUEST)

    Inspiration.objects.filter(follower=request.user, followed_id=user_id).delete()
    return Response({'message': 'You have unfollowed this user.'}, status=status.HTTP_200_OK)


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
    responses={201: 'Created'}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsVerifiedUser])
@parser_classes([MultiPartParser])
def create_post(request):
    title = request.data.get('title')
    image_or_fbx = request.FILES.get('image_or_fbx')
    user_id = request.user.id
    
    if not title:
        return Response({'message': 'Title is required.'}, status=status.HTTP_400_BAD_REQUEST)

    post_data = {'title': title, 'user': user_id}  # Use 'user' instead of 'user_id'
    serializer = PostSerializer(data=post_data)
    
    if serializer.is_valid():
        serializer.save()
        
        if image_or_fbx:
            # Generate a unique filename using UUID
            new_filename = f"{uuid.uuid4()}{os.path.splitext(image_or_fbx.name)[-1]}"

            # Initialize Firebase Storage client
            storage_client = storage.Client()

            # Upload the image to Firebase Storage
            bucket = storage_client.bucket('exinart-13556.appspot.com')
            blob = bucket.blob(f"posts_images/{new_filename}")
            blob.upload_from_string(image_or_fbx.read(), content_type=image_or_fbx.content_type)

            # Get the Direct Google Cloud Storage URL
            direct_url = blob.generate_signed_url(
                version="v4",
                expiration=datetime.timedelta(minutes=15),
                method="GET",
            )

            # Update the post with the image URL
            post = serializer.instance
            post.image_or_fbx = direct_url
            post.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
            description='Bearer <access_token>'
        )
    ],
     responses={200: 'Post list'}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_posts_list(request, user_id):
    try:
        user = CustomUser.objects.get(pk=user_id)
        posts = Post.objects.filter(user=user)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    

##TODO: Requires testing

@swagger_auto_schema(
    method='POST',
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
            description='Bearer <access_token>'
        )
    ],
    responses={201: 'Post loved successfully'}
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsVerifiedUser])
def like_post(request, post_id):

    """
    Love a post.
    
    Provide the post_id to love a post.

    Returns:
        Response: A message indicating whether the post was loved successfully.
    """
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return Response({'message': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    user = request.user
    try:
        like, created = Like.objects.get_or_create(user=user, post=post)
    except Exception as e:
        print("Error:", e)
    if created:
        return Response({'message': 'Post loved successfully.'}, status=status.HTTP_201_CREATED)
    return Response({'message': 'You already loved this post.'}, status=status.HTTP_400_BAD_REQUEST)

#create an unlike view
@swagger_auto_schema(
    method='POST',
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={200: 'Post unloved successfully'}
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsVerifiedUser])
def unlike_post(request, post_id):
    """
    Unlove a post.
    
    Provide the post_id to unlove a post.

    Returns:
        Response: A message indicating whether the post was unloved successfully.
    """
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return Response({'message': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    user = request.user
    try:
        Like.objects.get(user=user, post=post).delete()
    except Like.DoesNotExist:
        return Response({'message': 'You have not loved this post.'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': 'Post unloved successfully.'}, status=status.HTTP_200_OK)



@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={200: 'Post unloved successfully'}
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsVerifiedUser])
def get_likes_count_of_post(request, post_id):
    likes_count = Like.objects.filter(post__id=post_id).count()
    return Response({"likes_count": likes_count}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='POST',
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
            description='Bearer <access_token>'
        )
    ],
    request_body=CommentSerializer,
    responses={201: CommentSerializer()}
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsVerifiedUser])
def comment_post(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return Response({'message': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)

    text = request.data.get('text')
    comment = Comment.objects.create(user=request.user, post=post, text=text)
    serializer = CommentSerializer(comment)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={200: 'Post unloved successfully'}
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsVerifiedUser])
def get_comment_count_for_post(request, post_id):
    """
    Get comment count for a post.
    
    Provide the post_id to retrieve the comment count for a post.

    Returns:
        Response: The comment count.
    """
    comment_count = Comment.objects.filter(post__id=post_id).count()
    return Response({'comment_count': comment_count}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={200: 'Post unloved successfully'}
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsVerifiedUser])
def get_total_likes_for_user(request):
    """
    Get total number of likes for the user.
    
    Returns:
        Response: The total number of likes for the user.
    """
    total_likes = Like.objects.filter(user=request.user).count()
    return Response({'total_likes': total_likes}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={200: 'Post unloved successfully'}
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsVerifiedUser])
def get_total_comments_for_user(request):
    """
    Get total number of comments for the user.
    
    Returns:
        Response: The total number of comments for the user.
    """
    total_comments = Comment.objects.filter(user=request.user).count()
    return Response({'total_comments': total_comments}, status=status.HTTP_200_OK)



@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={200: 'Post unloved successfully'}
)
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsVerifiedUser])
@api_view(['GET'])
def list_all_posts(request):
    """
    List all posts with pagination.

    Returns:
        Response: Paginated list of posts.
    """
    paginator = CustomPagination()
    posts = Post.objects.all()
    paginated_posts = paginator.paginate_queryset(posts, request)
    serializer = PostSerializer(paginated_posts, many=True)
    return paginator.get_paginated_response(serializer.data)


class CustomPagination(PageNumberPagination):
    page_size = 10  # Adjust the page size as needed
    page_size_query_param = 'page_size'
    max_page_size = 100