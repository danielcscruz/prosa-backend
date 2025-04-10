from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following')
    groups = models.ManyToManyField('auth.Group',related_name="customuser_set",blank=True)
    user_permissions = models.ManyToManyField('auth.Permission',related_name="customuser_set",blank=True)

    def __str__(self):
        return self.username

class Post(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(max_length=280, blank=True, null=True)  # Pode ser um post normal ou um repost
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(CustomUser, related_name="liked_posts", blank=True)
    dislikes = models.ManyToManyField(CustomUser, related_name="disliked_posts", blank=True)
    repost = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="reposts")

    def __str__(self):
        if self.repost:
            return f"{self.user.username} reposted: {self.repost.user.username} - {self.repost.content[:50]}"
        return f"{self.user.username}: {self.content[:50]}"
