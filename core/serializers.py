from rest_framework import serializers
from .models import CustomUser, Post


class UserSerializer(serializers.ModelSerializer):
    followers_count = serializers.IntegerField(source='followers.count', read_only=True)
    following_count = serializers.IntegerField(source='following.count', read_only=True)
    posts_count = serializers.IntegerField(source='posts.count', read_only=True) 
    avatar = serializers.SerializerMethodField() 
    name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'name','username', 'email', 'posts_count','followers_count', 'following_count', 'avatar']

    def get_avatar(self,obj):
        request = self.context.get("request")

        if obj.avatar:
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url 
        return None 
    
    def get_name(self, obj):
        """Concatenates first and last name"""
        first_name = obj.first_name or ""
        last_name = obj.last_name or ""
        return f"{first_name} {last_name}".strip()

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'avatar']  # email não incluso se não for editável


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password", "first_name", "last_name", "avatar"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        user.set_password(password)


        user.save()
        return user


class PostSerializer(serializers.ModelSerializer):
    repost = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username', read_only=True)
    name = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    bookmark = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    user_avatar = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    is_reposted = serializers.SerializerMethodField()


    class Meta:
        model = Post
        fields = ['id', 'user', 'name', 'username', 'user_avatar', 'content', 'created_at', 'likes', 'bookmark', 'repost','is_liked', 'is_bookmarked', 'is_reposted'  ]

    def create(self, validated_data):
        # Adiciona o usuário ao post
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def get_name(self, obj):
        """Concatenates first and last name"""
        first_name = obj.user.first_name or ""
        last_name = obj.user.last_name or ""
        return f"{first_name} {last_name}".strip()
    
    def get_user_avatar(self,obj):
        if obj.user.avatar:  # Ensure avatar exists
            return self.context['request'].build_absolute_uri(obj.user.avatar.url)
        return self.context['request'].build_absolute_uri('/media/avatars/default1.png')  
    
    def get_created_at(self, obj):
        return obj.created_at.strftime("%d/%m/%y - %H:%M")
    
    def get_likes(self, obj):
        return obj.likes.count()
    
    def get_bookmark(self, obj):
        return obj.bookmark.count()
    
    def get_repost(self, obj):
        """Se for um repost, retorna o conteúdo do post original."""
        if obj.repost:
            return {
                "id": obj.repost.id,
                "username": obj.repost.user.username,
                "content": obj.repost.content,
                "created_at": obj.repost.created_at
            }
    def get_is_liked(self, obj):
        user = self.context['request'].user
        return user in obj.likes.all() if user.is_authenticated else False

    def get_is_bookmarked(self, obj):
        user = self.context['request'].user
        return user in obj.bookmark.all() if user.is_authenticated else False

    def get_is_reposted(self, obj):
        user = self.context['request'].user
        return Post.objects.filter(user=user, repost=obj).exists() if user.is_authenticated else False
    
        return None
