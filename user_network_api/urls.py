from django.urls import path
from . import views

urlpatterns = [
    # ... your other API endpoints
    path('follow/<int:user_id>/', views.follow_user, name='follow-user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow-user'),
    path('create-post/', views.create_post, name='create-post'),
    path('user/<int:user_id>/posts/', views.user_posts_list, name='user-posts-list'),
    
    ##TODO: Requires testing
    path('love/<int:post_id>/', views.love_post, name='love-post'),
    path('likes/<int:post_id>/', views.get_likes_for_post, name='get-likes-for-post'),
    path('engage/<int:post_id>/', views.engage_post, name='engage-post'),
    path('comment_count/<int:post_id>/', views.get_comment_count_for_post, name='get-comment-count-for-post'),
    path('total_likes/', views.get_total_likes_for_user, name='get-total-likes-for-user'),
    path('total_comments/', views.get_total_comments_for_user, name='get-total-comments-for-user'),

]
