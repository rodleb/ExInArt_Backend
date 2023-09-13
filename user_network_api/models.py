from django.db import models
from users_api.models import CustomUser
from django.utils import timezone


# Create your models here.

class Inspiration(models.Model):
    follower = models.ForeignKey(CustomUser, related_name='followers', on_delete=models.CASCADE)
    followed = models.ForeignKey(CustomUser, related_name='followed', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.follower} follows {self.followed}'
    

class Post(models.Model):
    title = models.CharField(max_length=510)
    image_or_fbx = models.URLField( blank=True, null=True)
    created_at = models.DateTimeField( default=timezone.now)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=CustomUser.objects.first().id)

    def __str__(self):
        return self.title


class Like(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    

