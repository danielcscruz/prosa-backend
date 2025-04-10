from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Post

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "is_active", "is_staff")
    search_fields = ("username", "email")
    list_filter = ("is_active", "is_staff")

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("user", "content", "created_at")
    search_fields = ("content", "author__username")
    list_filter = ("created_at",)
