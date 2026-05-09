from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin interface for CustomUser model.
    Extends Django's built-in UserAdmin.
    """
    fieldsets = UserAdmin.fieldsets + (
        ('PRESEC Information', {
            'fields': ('year_group', 'role')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('PRESEC Information', {
            'fields': ('year_group', 'role')
        }),
    )
    
    list_display = ['username', 'email', 'get_full_name', 'year_group', 'role', 'is_staff']
    list_filter = UserAdmin.list_filter + ('role', 'year_group')
    search_fields = ['username', 'email', 'first_name', 'last_name', 'year_group']
    ordering = ['-date_joined']
