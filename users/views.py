from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.permissions import IsAuthenticated
from record_management.models import Account, Transaction
from django.db.models import Sum

from .models import User
from .serializers import *
from .permissions import IsAdminOrSelf, IsAdminRole
from .utils import message
from drf_yasg.utils import swagger_auto_schema

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    lookup_field = 'slug' 
    permission_classes = [IsAuthenticated, IsAdminOrSelf] # Only Admin HAVE permission to manage users and thier roles

    # This is the decorator used above the funtion to provide extra features 
    # AND this decorator is used to give description to the API on Swagger
    @swagger_auto_schema(operation_description="Get all users list")
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return message(True, "Users fetched successfully", serializer.data, status.HTTP_200_OK)
        except Exception as e:
            return message(False, str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
    # This is the decorator used above the funtion to provide extra features 
    # AND this decorator is used to give description to the API on Swagger
    @swagger_auto_schema(operation_description="Create a new user")
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return message(True, "User created successfully", serializer.data, status.HTTP_201_CREATED)
        return message(False, "Validation Error", serializer.errors, status.HTTP_400_BAD_REQUEST)
    

    # This is the decorator used above the funtion to provide extra features 
    # AND this decorator is used to give description to the API on Swagger
    @swagger_auto_schema(operation_description="Get a specific user by slug")
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return message(True, "User details fetched", serializer.data, status.HTTP_200_OK)
        except Exception:
            return message(False, "User not found", status_code=status.HTTP_404_NOT_FOUND)

    # This is the decorator used above the funtion to provide extra features 
    # AND this decorator is used to give description to the API on Swagger
    @swagger_auto_schema(operation_description="Update user by slug")
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            if serializer.is_valid():
                serializer.save()
                return message(True, "User updated successfully", serializer.data, status.HTTP_200_OK)
            return message(False, "Validation Error", serializer.errors, status.HTTP_400_BAD_REQUEST)
        except Exception:
            return message(False, "User not found", status_code=status.HTTP_404_NOT_FOUND)

    # This is the decorator used above the funtion to provide extra features 
    # AND this decorator is used to give description to the API on Swagger
    @swagger_auto_schema(operation_description="Delete user by slug")
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            return message(True, "User deleted successfully", status_code=status.HTTP_200_OK)
        except Exception:
            return message(False, "User not found", status_code=status.HTTP_404_NOT_FOUND)
        

# Registration View (This creates user and sends the mail vo verification of the email )
class RegisterUserView(APIView):
    permission_classes = [] 

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # For Generating email  verification link  
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            current_site = get_current_site(request).domain
            relative_link = reverse('verify-email', kwargs={'uidb64': uid, 'token': token})
            absurl = f'http://{current_site}{relative_link}'

            # Message to be send in the mail of the user 
            email_body = f'Hi {user.username},\n\nPlease use the link below to verify your email and activate your account:\n{absurl}'
            
            try:
                send_mail(
                    subject='Verify your email for Finance Dashboard',  #subject of the mail
                    message=email_body,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except Exception as e:
                # delete user if email send fail to prvent user to retry 
                user.delete()
                return message(False, f"Failed to send email: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return message(True, "User created successfully. Please check your real email to verify your account.", serializer.data, status.HTTP_201_CREATED)
        
        return message(False, "Validation Error", serializer.errors, status.HTTP_400_BAD_REQUEST)

# Email Verification View
class VerifyEmailView(APIView):
    permission_classes = [] 

    def get(self, request, uidb64, token):
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not default_token_generator.check_token(user, token):
                return message(False, "Token is invalid or expired", status_code=status.HTTP_400_BAD_REQUEST)

            if user.is_active:
                return message(False, "Email is already verified", status_code=status.HTTP_400_BAD_REQUEST)

            # make user ACTIVE after successful verification
            user.is_active = True
            user.save()
            return message(True, "Email successfully verified. You can now login.", status_code=status.HTTP_200_OK)

        except User.DoesNotExist:
            return message(False, "User not found", status_code=status.HTTP_404_NOT_FOUND)
        except Exception:
            return message(False, "Invalid request", status_code=status.HTTP_400_BAD_REQUEST)


class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            return message(True, "Login successful", response.data, status_code=status.HTTP_200_OK)
        except Exception:
            return message(False, "Invalid credentials or email not verified. Please check your email.", status_code=status.HTTP_401_UNAUTHORIZED)
        
    


class AdminUserDirectoryView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        try:
            users = User.objects.all().order_by('-date_joined')
            user_list = []

            for user in users:
                user_accounts_count = Account.objects.filter(user=user).count()
                
                # ORM to show the exact final amount of the user in the user detail 
                user_txns = Transaction.objects.filter(user=user)
                income = user_txns.filter(type='INCOME').aggregate(Sum('amount'))['amount__sum'] or 0
                expense = user_txns.filter(type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or 0
                
                # net balance of user 
                real_balance = float(income - expense)
                
                user_list.append({
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "is_active": user.is_active,
                    "slug": user.slug,
                    "date_joined": user.date_joined.strftime("%Y-%m-%d"),
                    "stats": {
                        "total_accounts": user_accounts_count,
                        "current_balance": real_balance 
                    }
                })

            return message(True, "All users directory fetched successfully", user_list)
        
        except Exception as e:
            return message(False, str(e), status_code=500)