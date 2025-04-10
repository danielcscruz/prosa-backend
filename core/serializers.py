from rest_framework import serializers
from .models import CustomUser, Post

class UserSerializer(serializers.ModelSerializer):
    followers_count = serializers.IntegerField(source='followers.count', read_only=True)
    following_count = serializers.IntegerField(source='following.count', read_only=True)
    posts_count = serializers.IntegerField(source='posts.count', read_only=True) 

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'posts_count','followers_count', 'following_count']

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    repost = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'created_at', 'likes', 'dislikes', 'repost']

    def get_repost(self, obj):
        """Se for um repost, retorna o conteúdo do post original."""
        if obj.repost:
            return {
                "id": obj.repost.id,
                "author": obj.repost.author.username,
                "content": obj.repost.content,
                "created_at": obj.repost.created_at
            }
        return None
