from wsgiref import validate
from django.shortcuts import get_object_or_404, render
from .models import Bank, Transaction
from .serializers import BankSerializer, TransactionSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from django_filters import FilterSet, rest_framework as filters
from django.db.models import Sum
from django.db import transaction
from dateutil.relativedelta import relativedelta

# Create your views here.

class BankViewSet(viewsets.ModelViewSet):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer

class TransactionFilter(FilterSet):
    year = filters.NumberFilter(field_name='transaction_date', lookup_expr='year')
    month = filters.NumberFilter(field_name='transaction_date', lookup_expr='month')

    class Meta:
        model = Transaction
        fields = ['transaction_date', 'year', 'month']

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = TransactionFilter

    def list(self, request, *args, **kwargs):
        return_value = {
            "transactions": []
        }
        
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page if page is not None else queryset, many=True)
        summary_flag = request.query_params.get("summary")
        summary_flag_value = summary_flag is not None and summary_flag.lower() in ("1","true","t","yes","on")
        
        return_value['transactions'] = serializer.data
        
        if summary_flag_value:
            total_expenses = queryset.filter(transaction_type='E').aggregate(v=Sum('amount'))['v'] or 0
            total_revenues = queryset.filter(transaction_type='R').aggregate(v=Sum('amount'))['v'] or 0
            balance = total_revenues - total_expenses
                        
            return_value['summary'] = {
                "total_expenses": total_expenses,
                "total_revenues": total_revenues,
                "balance": balance
            }

            if page is not None:
                # Preserve pagination keys
                return self.get_paginated_response(return_value)

            return Response(return_value)
        
        # Default DRF behavior if no summary requested
        return self.get_paginated_response(return_value) if page is not None else Response(return_value)
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
         # The rest of this method is the default DRF implementation:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        created_transactions = []

        if validated_data['is_payed']:
            validated_data.pop('is_payed', None)

        if validated_data['transaction_type'] == 'E':
            installments = int(validated_data['total_installments'])
            
            if installments and installments > 1:
                # Create multiple installments
                base_date = validated_data.get('transaction_date')
                base_due_date = validated_data.get('due_date')
                
                for i in range(1, installments + 1):
                    transaction_data = validated_data.copy()
                    transaction_data['current_installment'] = i
                    transaction_data['total_installments'] = installments
                    # Increment date by month for each installment
                    transaction_data['transaction_date'] = base_date + relativedelta(months=i-1)
                    transaction_data['due_date'] = base_due_date + relativedelta(months=i-1)
                    
                    transaction = Transaction.objects.create(**transaction_data)
                    created_transactions.append(transaction)
            else:
                # Single transaction
                if installments == 1:
                    validated_data['current_installment'] = 1
                    validated_data['total_installments'] = 1
                
                transaction = Transaction.objects.create(**validated_data)
                created_transactions.append(transaction)
        else:
            transaction = Transaction.objects.create(**validated_data)
            created_transactions.append(transaction)

        # Serialize all created transactions
        response_serializer = self.get_serializer(created_transactions, many=True)
        headers = self.get_success_headers(response_serializer.data)
        
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)