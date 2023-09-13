# serializers.py
from rest_framework import serializers
from .models import Inspiration, Post, Like, Comment

class InspirationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inspiration
        fields = ['followed']

    def create(self, validated_data):
        request = self.context.get('request')
        follower = request.user
        followed = validated_data['followed']
        return Inspiration.objects.create(follower=follower, followed=followed)



from .models import Inspiration, Post, Like, Comment

class PostSerializer(serializers.ModelSerializer):
    is_liked = serializers.SerializerMethodField()
    is_commented = serializers.SerializerMethodField()
    is_followed = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['title', 'image_or_fbx', 'created_at', 'user', 'is_liked', 'is_commented', 'is_followed']

    def get_is_liked(self, obj):
        user = self.context.get("user")
        if user:
            return Like.objects.filter(user=user, post=obj).exists()
        return False

    def get_is_commented(self, obj):
        user = self.context.get("user")
        if user:
            return Comment.objects.filter(user=user, post=obj).exists()
        return False

    def get_is_followed(self, obj):
        user = self.context.get("user")
        if user:
            return Inspiration.objects.filter(follower=user, followed=obj.user).exists()
        return False



class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

class UnlikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
