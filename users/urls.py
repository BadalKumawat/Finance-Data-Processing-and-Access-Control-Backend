from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', RegisterUserView.as_view(), name='register'),
    path('auth/login/', CustomLoginView.as_view(), name='login'),
    path('auth/verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='verify-email'),

    # URL to list all the details of all the user Accessed only by role = ADMIN
    path('directory/all-users/', AdminUserDirectoryView.as_view(), name='admin-all-users'),
]