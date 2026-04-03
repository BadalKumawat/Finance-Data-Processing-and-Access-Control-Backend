from rest_framework import serializers
from django.db import transaction as db_transaction # For atomic updates
from .models import Category, Account, Transaction

class CategorySerializer(serializers.ModelSerializer):
    type = serializers.CharField()
    class Meta:
        model = Category
        fields = ['name', 'type', 'slug']
        read_only_fields = ['slug']

    def validate_type(self, value):
        value = value.upper() # user send anything it convert that into uppercase to prevent case sensityvity issue 
        if value not in ['INCOME', 'EXPENSE']:
            raise serializers.ValidationError("Type must be either INCOME or EXPENSE.")
        return value


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['name', 'balance', 'slug']
        read_only_fields = ['slug', 'balance'] # Balance update by transaction not Manually 


class TransactionSerializer(serializers.ModelSerializer):
    account = serializers.SlugRelatedField(slug_field='slug', queryset=Account.objects.all())
    category = serializers.SlugRelatedField(slug_field='slug', queryset=Category.objects.all())
    
    account_name = serializers.CharField(source='account.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    type = serializers.CharField()

    class Meta:
        model = Transaction
        fields = [
            'slug', 'account', 'account_name', 'category', 'category_name', 
            'amount', 'type', 'date', 'payment_method', 'description', 'created_at'
        ]
        read_only_fields = ['slug', 'created_at']

    def validate_type(self, value):
        value = value.upper()
        if value not in ['INCOME', 'EXPENSE']:
            raise serializers.ValidationError("Type must be either INCOME or EXPENSE.")
        return value
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def create(self, validated_data):
        # atomic() ensure ROLLBACK means if error occured database remains same o changed to database 
        with db_transaction.atomic():
            account = Account.objects.select_for_update().get(id=validated_data['account'].id)
            amount = validated_data['amount']
            txn_type = validated_data['type']

            # check that Category type matches to the Transaction type to prevent mismatch and wrong updates and wrong transaction
            if validated_data['category'].type != txn_type:
                raise serializers.ValidationError({"category": "Category type and Transaction type must match."})

            # Check Balance for Expense 
            if txn_type == 'EXPENSE':
                if account.balance < amount:
                    raise serializers.ValidationError({"amount": f"Insufficient funds. Account balance is only ₹{account.balance}."})
                account.balance -= amount
            
            # Add Balance for Income
            elif txn_type == 'INCOME':
                account.balance += amount
            
            account.save() # Update Balance
            
            # Creates the transaction
            return super().create(validated_data)