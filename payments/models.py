from django.db import models
from django.db.models.fields import related
from userauth.models import *
from pool.models import *

def upload_document_to(instance, filename):
    import os
    from django.utils.timezone import now
    filename_base, filename_ext = os.path.splitext(filename)
    return 'DocumentImages/%s' % (
    str(instance.phone)+'.jpg'
    )

# Create your models here.
class CustomerUrl(models.Model):
    phone = models.ForeignKey(User, on_delete=models.CASCADE)
    customerUrl = models.CharField(max_length=255, unique=True)
    documentUrl = models.CharField(max_length=255, unique=True, null=True, blank=False)
    funding_src = models.CharField(max_length=255, unique=True, null=True, blank=False)
    document = models.ImageField(upload_to=upload_document_to, editable=True, null=False, blank=False)
    documentType = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        phone = self.phone
        return str(phone)

class Transaction(models.Model):
    poolId = models.ForeignKey(CreatePool, on_delete=models.CASCADE)
    phone = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.CharField(max_length=20)
    paidTime = models.DateTimeField(auto_now_add=True)
    transactionUrl = models.CharField(max_length=255, unique=True)
    transactionStatus = models.BooleanField(default=False)
    lateTransactionStatus = models.BooleanField(default=False)
    payDate = models.DateTimeField(blank=True, null=True)
    loanPayment = models.BooleanField(default=False)
    def __str__(self):
        phone = self.phone
        return str(phone)

class NotPaid(models.Model):
    poolId = models.ForeignKey(CreatePool, on_delete= models.CASCADE)
    phone = models.ForeignKey(User, on_delete = models.CASCADE)
    amount = models.CharField(max_length=20,blank=False)
    payDate = models.DateTimeField(blank=True,null=True)
    uniqueId = models.CharField(max_length=20, unique=True, blank=False)
    paid = models.BooleanField(default=False)
    
    def __str__(self):
        phone = self.phone
        return str(phone)

#loan
class LoanDetail(models.Model):
    interest = models.FloatField(default=5)
    paidBy = models.CharField(max_length=20,default='Jamiie Account')

    def __str__(self):
        return self.paidBy

class Loan(models.Model):
    amount = models.IntegerField(blank=False, null= False)
    phone = models.ForeignKey(User,on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)
    poolId = models.ForeignKey(CreatePool,on_delete=models.CASCADE)
    transactionId = models.CharField(max_length=20, unique=True, blank=False, null=False)
    paid = models.BooleanField(default=False)
    approved = models.BooleanField(default= False)
    declined = models.BooleanField(default=False)
    def __str__(self):
        user = self.phone
        return str(user)

class ServerStat(models.Model):
    timeStamp = models.DateTimeField(auto_now_add=True)
    ram = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    def __str__(self):
        return str(self.ram)