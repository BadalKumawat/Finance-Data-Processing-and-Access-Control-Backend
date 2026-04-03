from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
import uuid

class User(AbstractUser):
    ROLE_CHOICES = (
        ('Viewer', 'VIEWER'),
        ('Analyst', 'ANALYST'),
        ('Admin', 'ADMIN'),
    )

    full_name= models.CharField(max_length=50, blank=True, null=True)
    email= models.EmailField(unique=True, error_messages={'unique':"This email is already in used Enter another email"})
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='VIEWER')
    slug = models.SlugField(max_length=255, unique=True, blank=True)


    USERNAME_FIELD = 'email'  # this is used to setup that now login will be with the help of email and pasword instead of username and password
    REQUIRED_FIELDS = ['username']

    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.username)
            self.slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} - {self.role}"