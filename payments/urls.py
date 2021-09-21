"""practiceapi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('bank/<str:id>',BankApi.as_view(), name='bank'),
    path('fundingsrc',FundingSourceApi.as_view(), name = 'funding source'),
    path('transfer',TransactionApi.as_view(), name='transfer money'),
    path('paiddetail',PaidUserApi.as_view(),name = 'paid detail'),
    path('notpaiddetail',NotPaidUserApi.as_view(), name = 'not paid detail'),
    path('adminpaidusers',AdminPaidUsers.as_view(), name = 'admin paid users'),
    path('adminnotpaidusers',AdminNotPaidUsers.as_view(), name = 'admin not paid users'),
    path('bankverification',BankVerificationApi.as_view(), name = 'bank verification'),
    path('amount',AmountApi.as_view(), name = 'amount'),
    path('loan',LoanApi.as_view(), name = 'loan'),
    path('loandetail',LoanDetailApi.as_view(), name= 'loan detail'),
    path('paybutton',PayButtonApi.as_view(), name = 'pay button'),
    path('loanrequests',LoanRequestApi.as_view(), name = 'loan requests'),
    path('loanapproval',LoanApprovalApi.as_view(), name = 'loan approval'),
    path('loandeclined',LoanDeclineApi.as_view(), name = 'loan declined'),
    path('transactions',JamiieTransactionsApi.as_view(), name = 'transactions list'),
    path('jamiiepaidusers/<str:id>',JamiiePaidUsers.as_view(), name = 'jamiie paid users'),
    path('transactiondetail',TransactionDetailApi.as_view(),name = 'transaction detail'),
    path('loandeclinedlist', LoanDeclinedListApi.as_view(), name = 'Loan declined list'),
    path('loanpaidlist', LoanPaidListApi.as_view(), name = 'loan paid list'),
    path('loannotpaidlist',LoanNotPaidListApi.as_view(), name = 'loan not paid list'),
    path('loanlist',LoanListApi.as_view(), name = 'loan list'),
    path('repayloan',RepayLoanApi.as_view(), name = 'repay loan'),
    path('weeklynotpaid',DifferentiateWeeklyNotPaid.as_view(),name='Weekly Not Paid'),
    path('monthlynotpaid',DifferentiateMonthlyNotPaid.as_view(),name='Monthly Not Paid'),
    path('cronjob',CronJob.as_view(), name='cron job'),
]