from django.db import models

# Create your models here

class Bank(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Transaction(models.Model):
    def __str__(self):
        return self.description
    
    TRANSACTION_TYPE = [
        ('E', 'Expense'),
        ('R', 'Revenue'),
    ]

    PAYMENT_TYPE = [
        ('D', 'Debit'),
        ('C', 'Credit'),
    ]
    
    transaction_type = models.CharField(max_length=1,choices=TRANSACTION_TYPE)
    description = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    due_date = models.DateField(blank=True,null=True)
    transaction_date = models.DateField()
    annotations = models.TextField(blank=True,null=True)
    payment_type = models.CharField(blank=True,null=True,max_length=1,choices=PAYMENT_TYPE)
    bank = models.ForeignKey(Bank,on_delete=models.PROTECT,related_name="transactions")
    is_payed = models.BooleanField(default=False)
    is_received = models.BooleanField(default=False)
    current_installment = models.IntegerField(null=True,blank=True)
    total_installments = models.IntegerField(null=True,blank=True)
    is_salary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
