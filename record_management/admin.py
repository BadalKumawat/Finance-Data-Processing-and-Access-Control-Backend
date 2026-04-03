from django.contrib import admin
from .models import Category, Account, Transaction

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'slug')
    list_filter = ('type',)
    search_fields = ('name', 'slug')
    readonly_fields = ('slug',) 

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'balance', 'slug')
    search_fields = ('name', 'slug', 'user__username', 'user__email')
    readonly_fields = ('slug',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('slug', 'user', 'account', 'category', 'amount', 'type', 'date')
    list_filter = ('type', 'date', 'payment_method')
    search_fields = ('slug', 'description', 'user__username', 'account__name', 'category__name')
    readonly_fields = ('slug', 'created_at')