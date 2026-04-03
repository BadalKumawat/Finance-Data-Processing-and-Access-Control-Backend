from django.db import models
from django.conf import settings
from django.utils.text import slugify
import uuid

# CATEGORY MODEL
class Category(models.Model):
    TYPE_CHOICES = (('INCOME', 'Income'), ('EXPENSE', 'Expense'))
    
    name = models.CharField(max_length=50) # Food, Salary
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.type}-{self.name}-{uuid.uuid4().hex[:6]}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.type})"


# ACCOUNT MODEL
class Account(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=100) # SBI Bank, HDFC Bank
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{uuid.uuid4().hex[:8]}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - ₹{self.balance}"


# TRANSACTION MODEL  CORE model for Record Mangement 
class Transaction(models.Model):
    PAYMENT_METHODS = (('CASH', 'Cash'), ('UPI', 'UPI'), ('BANK', 'Bank Transfer'))
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.RESTRICT) # RESTRICT to prevent category from deleting if it is in used 
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=10, choices=Category.TYPE_CHOICES)
    date = models.DateField()
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHODS, default='UPI')
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"txn-{self.type}-{uuid.uuid4().hex[:10]}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.slug} | {self.amount}"