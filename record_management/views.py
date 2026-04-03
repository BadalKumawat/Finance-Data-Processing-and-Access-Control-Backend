from rest_framework import viewsets, status
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Account, Transaction
from .serializers import CategorySerializer, AccountSerializer, TransactionSerializer
from .permissions import IsOwnerAdminOrAnalyst
from users.utils import message
from rest_framework.views import APIView
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from rest_framework.filters import SearchFilter
from users.pagination import CustomPagination

# CATEGORY VIEWSET
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsOwnerAdminOrAnalyst] 
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return message(True, "Categories fetched", serializer.data)

# ACCOUNT VIEWSET
class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    lookup_field = 'slug'
    permission_classes = [IsOwnerAdminOrAnalyst]

    # Applied data validation that a user can only see data of its own not any other user 
    def get_queryset(self):
        user = self.request.user
        user_role = user.role.upper() if user.role else ''

        if user_role in ['ADMIN', 'ANALYST']:
            return Account.objects.all()
        return Account.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # make owner to user who has made an account 

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return message(True, "Accounts fetched", serializer.data)

# TRANSACTION VIEWSET
class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    lookup_field = 'slug'
    permission_classes = [IsOwnerAdminOrAnalyst]
    
    pagination_class = CustomPagination

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['type', 'category__slug', 'account__slug', 'date']

    search_fields = ['description', 'category__name', 'account__name']

    def get_queryset(self):
        user = self.request.user

        user_role = user.role.upper() if user.role else ''

        if user_role in ['ADMIN', 'ANALYST']:
            return Transaction.objects.all().order_by('-date')
        return Transaction.objects.filter(user=user).order_by('-date')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())


        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return message(True, "Transactions fetched", serializer.data)
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return message(True, "Transaction successful", serializer.data, status.HTTP_201_CREATED)
        return message(False, "Validation Error", serializer.errors, status.HTTP_400_BAD_REQUEST)
    

class DashboardSummaryView(APIView):

    permission_classes = [IsAuthenticated] 

    @swagger_auto_schema(operation_description="Get Dashboard Analytics and Summaries")
    def get(self, request, *args, **kwargs):
        user = request.user
        user_role = user.role.upper() if user.role else 'VIEWER'

        if user_role == 'VIEWER':
            # Access validation that a user can see its own data not any other user data 
            base_query = Transaction.objects.filter(user=user)
        
        elif user_role in ['ADMIN', 'ANALYST']:
            # Admin/Analyst can see any user data by passing slug in url in Backend 
            target_user_slug = request.GET.get('user_slug')
            if target_user_slug:
                base_query = Transaction.objects.filter(user__slug=target_user_slug)
            else:
                # If no slug then data or all the user will be shown here 
                base_query = Transaction.objects.all()

        # CALCULATIONS using django ORM 
        
        # Total Income, Expenses & Net Balance
        # Aggregate for fetching sum of number directly from database 
        income_agg = base_query.filter(type='INCOME').aggregate(total=Sum('amount'))['total']
        expense_agg = base_query.filter(type='EXPENSE').aggregate(total=Sum('amount'))['total']
        
        total_income = income_agg if income_agg else 0
        total_expense = expense_agg if expense_agg else 0
        net_balance = total_income - total_expense

        # Category Wise Totals
        # Annotate work like GROUP BY of SQL 
        category_wise = base_query.values(
            'category__name', 'type'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('-total_amount')

        # Monthly Trends
        # TruncMonth converts date to month for analysis
        monthly_trends = base_query.annotate(
            month=TruncMonth('date')
        ).values(
            'month', 'type'
        ).annotate(
            total=Sum('amount')
        ).order_by('month')

        # Recent Activity Last 5 transactions
        recent_transactions = base_query.order_by('-created_at')[:5]
        recent_activity_data = TransactionSerializer(recent_transactions, many=True).data

        dashboard_data = {
            "overview": {
                "total_income": total_income,
                "total_expenses": total_expense,
                "net_balance": net_balance
            },
            "category_wise_totals": list(category_wise),
            "monthly_trends": list(monthly_trends),
            "recent_activity": recent_activity_data
        }

        return message(True, "Dashboard summary fetched successfully", dashboard_data)