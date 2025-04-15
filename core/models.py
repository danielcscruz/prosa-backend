from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following')
    groups = models.ManyToManyField('auth.Group',related_name="customuser_set",blank=True)
    user_permissions = models.ManyToManyField('auth.Permission',related_name="customuser_set",blank=True)
    avatar = models.ImageField(upload_to="avatars/", default="/avatars/default1.png", blank=True, null=True)

    def __str__(self):
        return self.username

class Post(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(max_length=280, blank=True, null=True)  # Pode ser um post normal ou um repost
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(CustomUser, related_name="liked_posts", blank=True)
    bookmark = models.ManyToManyField(CustomUser, related_name="bookmarked_posts", blank=True)
    repost = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="reposts")

    def __str__(self):
        try:
            if self.repost:
                username = self.repost.user.username if self.repost.user else "usuário desconhecido"
                content = self.repost.content[:50] if self.repost.content else ""
                return f"{self.user.username} reposted: {username} - {content}"
        except Exception:
            return f"{self.user.username} reposted: conteúdo indisponível"
        return f"{self.user.username}: {self.content[:50] if self.content else ''}"

