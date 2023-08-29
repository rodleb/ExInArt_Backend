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



class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'image_or_fbx', 'created_at', 'user']


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
