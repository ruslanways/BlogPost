from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Post, Like



admin.site.register(Post)
admin.site.register(Like)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "date_joined", "last_login", "last_request", "is_staff", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('last_request',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('email',)}),
    )
