from rest_framework import serializers
from .models import *
from pool.serializers import *

class PaidDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

        
class NotPaidDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotPaid
        fields = '__all__'

class LoanApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class TransactionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('poolId','phone','amount','paidTime','transactionUrl','transactionStatus',)

class LoanListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ('poolId','phone','amount','transactionId','createdAt',)
