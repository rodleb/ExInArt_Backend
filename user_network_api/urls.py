from django.urls import path
from . import views

urlpatterns = [
    # ... your other API endpoints
    path('follow/<int:user_id>/', views.follow_user, name='follow-user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow-user'),
    path('create-post/', views.create_post, name='create-post'),
    path('user/<int:user_id>/posts/', views.user_posts_list, name='user-posts-list'),

    path('like/<int:post_id>/', views.like_post, name='like-post'),
    path('unlike/<int:post_id>/', views.unlike_post, name='unlike-post'),
    path('likes_count/<int:post_id>/', views.get_likes_count_of_post, name='get-likes-for-post'),

    path('comment/<int:post_id>/', views.comment_post, name='engage-post'),
    path('comment_count/<int:post_id>/', views.get_comment_count_for_post, name='get-comment-count-for-post'),

    path('posts_list/', views.list_all_posts, name='list-all-posts'),

    ##TODO: Requires testing
    path('total_likes/', views.get_total_likes_for_user, name='get-total-likes-for-user'),
    path('total_comments/', views.get_total_comments_for_user, name='get-total-comments-for-user'),

]
