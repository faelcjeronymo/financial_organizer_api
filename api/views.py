from django.shortcuts import render
from .models import Bank, Transaction
from .serializers import BankSerializer, TransactionSerializer
from rest_framework import viewsets

# Create your views here.

class BankViewSet(viewsets.ModelViewSet):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer