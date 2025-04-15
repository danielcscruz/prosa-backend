from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import CustomUser, Post

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "is_active", "is_staff", "avatar")
    search_fields = ("username", "email")
    list_filter = ("is_active", "is_staff")

    readonly_fields = ("avatar_preview",)


    fieldsets = UserAdmin.fieldsets + (
        ("Perfil Personalizado", {
            "fields": ("avatar", "avatar_preview", "followers")
        }),
    )
    filter_horizontal = ("followers", "groups", "user_permissions")

    
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:50%;"/>', obj.avatar.url)
        return "(Sem imagem)"

    avatar_preview.short_description = "Prévia do Avatar"

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("user", "content", "created_at")
    search_fields = ("content", "username")
    list_filter = ("created_at",)
