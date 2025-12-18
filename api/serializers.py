from rest_framework import serializers
from .models import Transaction, Bank

class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    # For read operations, use the BankSerializer to show nested bank details.
    bank = BankSerializer(read_only=True)       
    # For write operations, accept a bank ID.
    bank_id = serializers.PrimaryKeyRelatedField(queryset=Bank.objects.all(), source='bank', write_only=True)

    class Meta:
        model = Transaction
        fields = [field.name for field in Transaction._meta.get_fields()] + ['bank_id']