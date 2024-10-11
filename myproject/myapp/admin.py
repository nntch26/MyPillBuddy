from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import *

# Customize the UserAdmin to add first_name and last_name fields
class CustomUserAdmin(BaseUserAdmin):
    # Add first_name and last_name to the add_fieldsets
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'password1', 'password2'),
        }),
        ('Add Groups', {
            'fields': ('groups',),
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_active'),
        }),
    )

    # This will also display first_name and last_name in the change form
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Password Reset', {'fields': ('last_login', 'date_joined')}),
    )

# Unregister the original UserAdmin
admin.site.unregister(User)
# Register the customized UserAdmin
admin.site.register(User, CustomUserAdmin)

@admin.register(Patient)
class UserDetailAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'birth_date')
    search_fields = ('user__first_name', 'user__last_name')
    list_filter = ('gender',)