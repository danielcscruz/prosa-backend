from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.pagination import PageNumberPagination  # Ou LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q

from django.shortcuts import get_object_or_404

from .models import CustomUser, Post
from .serializers import UserSerializer, PostSerializer, UserRegisterSerializer, UserUpdateSerializer
from django.db.models import Count

# Defina a classe de paginação
class PostPagination(PageNumberPagination):
    page_size = 10  # Número de itens por página
    page_size_query_param = 'page_size'  # Permite que o cliente especifique o tamanho da página via query string
    max_page_size = 100  # Limita o tamanho máximo da página

class CustomUserViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar usuários"""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['get', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user

        if request.method == 'GET':
            serializer = UserSerializer(user, context={'request': request})
            return Response(serializer.data)

        elif request.method == 'PATCH':
            serializer = UserUpdateSerializer(user, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)

        
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticatedOrReadOnly],  url_path='profile/(?P<username>[^/.]+)')
    def profile(self, request, username=None):

        user = get_object_or_404(CustomUser, username=username)
        avatar_url = user.avatar.url if user.avatar else "/default-avatar.png"
        if user.avatar:
            avatar_url = request.build_absolute_uri(user.avatar.url)
        # Aqui você pode adicionar outras informações, como followers_count e following_count
        user_data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "avatar": avatar_url,  # Agora com o caminho absoluto
            "followers_count": user.followers.count(),  # Se você tem um campo followers
            "following_count": user.following.count(),   # Se você tem um campo following
            "is_me": request.user == user,
            "is_following": request.user in user.followers.all() if request.user.is_authenticated else False
        }
        return Response(user_data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def follow(self, request, pk=None):
        target_user = self.get_object()
        user = request.user

        if user == target_user:
            return Response({"detail": "Você não pode seguir a si mesmo."}, status=400)

        if target_user in user.following.all():
            user.following.remove(target_user)
            return Response({"detail": "Unfollowed"}, status=204)
        else:
            user.following.add(target_user)
            return Response({"detail": "Followed"}, status=201)



class MostLikedPostsViewSet(viewsets.ModelViewSet):
    """listar os cinco posts mais curtidos"""
    queryset = Post.objects.annotate(like_count=Count('likes')).order_by('-like_count')[:4]
    serializer_class = PostSerializer

class RandomFollowersViewSet(viewsets.ModelViewSet):
    """listar cinco perfis aleatorios"""
    queryset = CustomUser.objects.order_by("?")[:4]
    serializer_class = UserSerializer



class UserRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Use UserSerializer to return full user info
            response_data = UserSerializer(user, context={'request': request}).data
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = PostPagination  # Aplica a paginação no ViewSet

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


    @action(detail=False, methods=['get'], url_path='feed', permission_classes=[IsAuthenticated])
    def feed(self, request):
        """Posts do usuário logado + pessoas que ele segue, incluindo reposts"""
        user = request.user
        following = user.following.all()

        # Posts originais OU reposts feitos por user ou pessoas que ele segue
        posts = Post.objects.filter(Q(user__in=[*following, user])).order_by('-created_at')

        # Paginação
        paginator = PostPagination()
        paginated_posts = paginator.paginate_queryset(posts, request)
        serializer = self.get_serializer(paginated_posts, many=True)
        return paginator.get_paginated_response(serializer.data)


    @action(detail=False, methods=['get'], url_path='user/(?P<username>[^/.]+)')
    def posts_by_user(self, request, username=None):
        """Posts criados ou repostados pelo usuário"""
        user = get_object_or_404(CustomUser, username=username)

        posts = Post.objects.filter(user=user).order_by('-created_at')

        # Paginação
        paginator = PostPagination()
        paginated_posts = paginator.paginate_queryset(posts, request)
        serializer = self.get_serializer(paginated_posts, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'], url_path='bookmark', permission_classes=[IsAuthenticated])
    def bookmarked_posts(self, request):
        """Posts salvos pelo usuário logado"""
        user = request.user
        posts = user.bookmarked_posts.all()

        # Paginação
        paginator = PostPagination()
        paginated_posts = paginator.paginate_queryset(posts, request)
        serializer = self.get_serializer(paginated_posts, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        if request.user in post.likes.all():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
        return Response(status=204)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def bookmark(self, request, pk=None):
        post = self.get_object()
        if request.user in post.bookmark.all():
            post.bookmark.remove(request.user)
        else:
            post.bookmark.add(request.user)
        return Response(status=204)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def repost(self, request, pk=None):
        original_post = self.get_object()
        repost_instance = Post.objects.filter(user=request.user, repost=original_post).first()

        if repost_instance:
            repost_instance.delete()
            return Response({"detail": "Repost removed"}, status=204)

        Post.objects.create(user=request.user, repost=original_post)
        return Response({"detail": "Repost created"}, status=201)
