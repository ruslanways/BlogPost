from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from django.conf import settings

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # model = settings.AUTH_USER_MODEL
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ("username", "date_joined", "last_login", "is_staff", "is_active")

# admin.site.register(CustomUser, CustomUserAdmin)
