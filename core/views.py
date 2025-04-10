from rest_framework import viewsets, permissions
from .models import CustomUser, Post
from .serializers import UserSerializer, PostSerializer

class CustomUserViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar usuários"""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class PostViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar posts"""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        """Define automaticamente o autor do post"""
        serializer.save(author=self.request.user)
