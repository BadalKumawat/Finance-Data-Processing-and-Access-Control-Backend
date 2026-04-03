from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    
    # LIST View this defines waht to show on the table in admin panel
    list_display = ('username', 'email', 'full_name', 'role', 'is_active','slug')
    
    # For filtering and Search
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'full_name')
    readonly_fields = ('slug',)
    
    # CHANGE VIEW of ADMIN panel 
    # here we are showing our custome field of model in admin panel instead of in built fields
    fieldsets = (
        ('Login Credentials', {
            'fields': ('username', 'password')
        }),
        ('Personal Information', {
            'fields': ('full_name', 'email', 'phone_number', 'city', 'state')
        }),
        ('Role & Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    # this from is used when creating new user form admin panel 
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1','password2', 'role', 'full_name', 'is_active', 'is_staff'),
        }),
    )

    # Admin panel se user banate time slug auto-generate karne ke liye
    # prepopulated_fields = {'slug': ('username',)}  #  removing this line because slug is auto generating inside our models.py file 


admin.site.register(User, CustomUserAdmin)