from pool.views import UserJoinedPoolApi
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .models import *
from payments.utilFunctions import *
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework import status
from rest_framework.authentication import *
from rest_framework.permissions import *
from dotenv import load_dotenv
from pathlib import Path
import json
import os
from rest_framework.pagination import PageNumberPagination
import datetime
env_file = Path('.') / '.env'
load_dotenv(dotenv_path=env_file)
from .serializers import *
from pool.models import *
from rest_framework.authtoken.models import Token
import random
# Create your views here.
def cookiesAuth(cookies):
    try:
        val = cookies
        count = 0
        for i in val:
            count=count+1
            if (count == 1):
                user = User.objects.get(phone = i)
                if Token.objects.filter(user=user).exists():
                    if str(Token.objects.get(user=user)) == str(val[i]):
                        return True
    except Exception as e:
        print(e)

def transactionIdGenerator():
    transactionId = random.randrange(1000000,10000000)
    return transactionId

def uniqueIdGenerator():
    uniqueId = random.randrange(10000,100000)
    return uniqueId

class BankVerificationApi(APIView):
    authentication_classes=[TokenAuthentication,]
    permission_classes = [IsAuthenticated,]
    try:
        def post(self, request):
            data = request.data
            phone = data['phone']
            user = CustomerUrl.objects.get(phone=phone)
            if user.funding_src == None:
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response({'response':'Bank already attached'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    except Exception as e:
        print(e)

class BankApi(APIView):
    authentication_classes = []
    permission_classes = []
    renderer_classes = [TemplateHTMLRenderer,]
    try:
        def get(self, request, id):
            phone = '+'+id
            user_url = CustomerUrl.objects.get(phone=phone).customerUrl
            i_av_token = get_iav_token(user_url)
            context = {
                'token': i_av_token,
                'phone': phone,
                'env': os.getenv('ENV')
            }
            return render(request, 'index.html', context)
    except Exception as e:
        print(e)
 
class FundingSourceApi(APIView):
    authentication_classes = []
    permission_classes = []
    try:
        def post(self, request):
            data = request.data
            print(data)
            phone = data['phone']
            funding_src = data['data']['_links']['funding-source']['href']
            user = CustomerUrl.objects.get(phone=phone)
            user.funding_src = funding_src
            user.save()
            user = User.objects.get(phone=phone)
            user.bankAdded = True
            user.save()
            return Response(status=status.HTTP_201_CREATED)

    except Exception as e:
        print(e)

class TransactionApi(APIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = [IsAuthenticated,]
    try:
        def post(self, request):
            day = datetime.datetime.now().strftime('%A')
            day = True
            if day == 'Friday':  #replace True with 'Friday'
                data = request.data
                phone = data['phone']
                poolId = data['poolId']
                amount = CreatePool.objects.get(poolId=poolId).contributionAmount
                funding_src = CustomerUrl.objects.get(phone=phone).funding_src
                transfer_body = {
                    '_links': {
                        'source': {
                            'href': os.getenv('JAMIIE_FUNDING_SRC')
                        },
                        'destination': {
                            'href': funding_src
                        }
                    },
                    'amount': {
                        'currency': 'USD',
                        'value': amount
                    },
                    'clearing': {
                        'destination': 'next-available'
                    }
                }
                transaction_url = initiate_transfer(transfer_body)
                poolId = CreatePool.objects.get(poolId=poolId)
                phone  = User.objects.get(phone=phone)
                Transaction.objects.create(poolId=poolId, phone=phone, amount=amount,transactionUrl=transaction_url,transactionStatus=True)
                response = {
                    "amount":amount,
                    "transaction_url":transaction_url
                }
                return Response(response,status=status.HTTP_200_OK)
            
            else:
                return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    except Exception as e:
        print(e)

'''
endpoint: /payments/paybutton
request type: GET
response: 
if Friday : {'payButton':True}, status : 200
else: {'payButton':False}, status : 405
'''
class PayButtonApi(APIView):
    authentication_classes=[TokenAuthentication,]
    permission_classes=[IsAuthenticated,]
    try:    
        def get(self,request):
            day = datetime.datetime.now().strftime('%A')
            if day == 'Friday':
                return Response({'payButton':True}, status=status.HTTP_200_OK)
            else:
                return Response({'payButton':False},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    except Exception as e:
        print(e)
#confirm payment: /payments/amount
class AmountApi(APIView):
    authentication_classes=[TokenAuthentication,]
    permission_classes=[IsAuthenticated,]
    try:
        def post(self,request):
            data = request.data
            poolId = data['poolId']
            amount = CreatePool.objects.get(poolId=poolId).contributionAmount
            return Response({'amount':amount},status = status.HTTP_200_OK)
    except Exception as e:
        print(e)

class PaidUserApi(APIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = [IsAuthenticated,]
    try:
        def post(self,request):
            data = request.data
            phone = data['phone']
            transactions = Transaction.objects.filter(phone=phone, transactionStatus=True, loanPayment=False)
            serializer = PaidDetailSerializer(transactions, many=True)
            return Response({'response':serializer.data},status=status.HTTP_200_OK)

    except Exception as e:
        print(e)

class NotPaidUserApi(APIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = [IsAuthenticated,]
    try:
        def post(self, request):
            data = request.data
            phone = data['phone']
            notPaid = NotPaid.objects.filter(phone=phone)
            serializer = NotPaidDetailSerializer(notPaid, many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
    except Exception as e:
        print(e)

class AdminPaidUsers(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    try:
        def post(self,request):
            data = request.data
            poolId = data['poolId']
            transactions = Transaction.objects.filter(poolId=poolId,loanPayment=False)
            serializer = PaidDetailSerializer(transactions, many=True)
            return Response({'response':serializer.data},status=status.HTTP_200_OK)

    except Exception as e:
        print(e) 

class AdminNotPaidUsers(APIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = [IsAuthenticated,]
    try:
        def post(self,request):
            data = request.data
            poolId = data['poolId']
            notPaid = NotPaid.objects.filter(poolId=poolId)
            serializer = NotPaidDetailSerializer(notPaid, many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
    
    except Exception as e:
        print(e)

class JamiiePaidUsers(APIView):
    authentication_classes = []
    permission_classes = []
    try:
        def get(self,request,id):
                cookies = request.COOKIES
                response = cookiesAuth(cookies)
                if response:
                    transactions = Transaction.objects.filter(poolId=id)
                    return Response(status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        print(e)

class JamiieNotPaidUsers(APIView):
    authentication_classes = []
    permission_classes = []
    try:
        def get(self,request,id):
                cookies = request.COOKIES
                response = cookiesAuth(cookies)
                if response:
                    transactions = NotPaid.objects.filter(poolId=id)
                    return Response(status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        print(e)
'''
endpoint: /payments/transactions
'''
class JamiieTransactionsApi(ListAPIView):
    queryset = Transaction.objects.all()
    authentication_classes = []
    permission_classes = []
    serializer_class = TransactionSerializer
    pagination_class = PageNumberPagination

    try:
        def get(self, request, *args, **kwargs):
            cookies = request.COOKIES
            response = cookiesAuth(cookies)
            if response:
                return self.list(request, *args, **kwargs)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        print(e)

#Loan Method
'''
request type : POST
endpoint: /payments/loandetail
data = {'poolId':'poolId'}
response: 'response':{'interest':5.0,'amount':'100'}
'''
class LoanDetailApi(APIView):
    authentication_classes=[TokenAuthentication,]
    permission_classes=[IsAuthenticated,]
    try:
        def post(self,request):
            data = request.data
            poolId = CreatePool.objects.get(poolId=data['poolId'])
            jamiie = LoanDetail.objects.all()
            interest = jamiie[0].interest  
            amount = int(poolId.contributionAmount *interest/100)
            response = {'interest':interest,'amount':amount}
            return Response({'response':response},status=status.HTTP_200_OK)  
    except Exception as e:
        print(e)

'''
Request type : POST
endpoint: /payments/loan
data = {'poolId':'poolId','phone':'+919816456565'}
response: {'response':'Your loan is successfully applied'}, status=200
'''
class LoanApi(APIView):
    authentication_classes=[TokenAuthentication,]
    permission_classes=[IsAuthenticated,]
    try:
        def post(self,request):
            data = request.data
            poolId = CreatePool.objects.get(poolId=data['poolId'])
            phone = User.objects.get(phone=data['phone'])
            jamiie = LoanDetail.objects.all()
            interest = jamiie[0].interest  
            amount = poolId.contributionAmount *interest/100 
            transactionId = transactionIdGenerator()
            Loan.objects.create(amount = int(amount), phone = phone, poolId=poolId, transactionId=transactionId)
            return Response({'response':'Your loan is successfully applied'}, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)

'''
Request Type: POST
endpoint : payments/loanlist
data = {'phone':'+919816456565'}
response : list, status = 200
'''
class LoanListApi(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]
    try:    
        def post(self,request):
            data = request.data
            phone = data['phone']
            loan_list = Loan.objects.filter(phone=phone,approved=True,paid=False)
            serializer = LoanListSerializer(loan_list, many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
'''
Request Type : POST
endpoint : /payments/repayloan
data = {'transactionId':'12345678'}
response : response = {
                    "amount":amount,
                    "transaction_url":transaction_url
                    "message":'Loan is successfully paid'
                },
            status = 200
'''
class RepayLoanApi(APIView):
    authentication_classes=[TokenAuthentication,]
    permission_classes= [IsAuthenticated,]
    try:
        def post(self,request):
            day = datetime.datetime.now().strftime('%A')
            day = True
            if day == True:  #replace True with 'Friday'
                data = request.data
                transactionId = data['transactionId']
                transaction = Loan.objects.get(transactionId=transactionId) 
                poolId = transaction.poolId
                amount = transaction.amount
                phone = transaction.phone
                funding_src = CustomerUrl.objects.get(phone=phone).funding_src
                transfer_body = {
                    '_links': {
                        'source': {
                            'href': os.getenv('JAMIIE_FUNDING_SRC')
                        },
                        'destination': {
                            'href': funding_src
                        }
                    },
                    'amount': {
                        'currency': 'USD',
                        'value': amount
                    },
                    'clearing': {
                        'destination': 'next-available'
                    }
                }
                transaction_url = initiate_transfer(transfer_body)
                poolId = CreatePool.objects.get(poolId=poolId)
                phone  = User.objects.get(phone=phone)
                Transaction.objects.create(poolId=poolId, phone=phone, amount=amount,transactionUrl=transaction_url,transactionStatus=True,loanPayment=True)
                transaction.paid = True
                transaction.save()
                response = {
                    "amount":amount,
                    "transaction_url":transaction_url,
                    "message":'Loan is successfully paid'
                }
                return Response(response,status=status.HTTP_200_OK)

            else:
                return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    except Exception as e:
        print(e)
'''
Request type : GET
endpoint: /payments/loanrequests
response : List of Requested Loans 
'''
class LoanRequestApi(ListAPIView):
    queryset = Loan.objects.filter(approved=False,declined=False,paid=False)
    authentication_classes = []
    permission_classes = []
    serializer_class = LoanApprovalSerializer
    pagination_class = PageNumberPagination

    try:
        def get(self, request, *args, **kwargs):
            cookies = request.COOKIES
            response = cookiesAuth(cookies)
            if response:
                return self.list(request, *args, **kwargs)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        print(e)

'''
Request type : POST
endpoint: /payments/loanapproval
data = {'transactionId':'1563441'}
status = 200
{'message':'Your loan is approved'}
'''
class LoanApprovalApi(APIView):
    authentication_classes=[]
    permission_classes=[]
    try:
        def post(self,request):
            cookies = request.COOKIES
            response = cookiesAuth(cookies)
            if response:
                data=request.data
                transactionId=data['transactionId']
                loan = Loan.objects.get(transactionId  = transactionId)
                loan.approved = True
                loan.save()
                phone = User.objects.get(phone=loan.phone)
                Transaction.objects.create(poolId=loan.poolId, phone=phone, amount=loan.amount,transactionUrl=transactionId,transactionStatus=True)
                return Response({'message':'Your loan is approved'},status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        print(e)

'''
Request type : POST
endpoint: /payments/loandeclined
data = {'transactionId':'1563441'}
status = 200
{'message':'Your loan is declined'}
'''
class LoanDeclineApi(APIView):
    authentication_classes=[]
    permission_classes=[]
    
    try:
        def post(self,request):
            cookies = request.COOKIES
            response = cookiesAuth(cookies)
            if response:
                data=request.data
                transactionId=data['transactionId']
                loan = Loan.objects.get(transactionId  = transactionId)
                loan.declined = True
                loan.save()
                return Response({'message':'Your loan is declined'},status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        print(e)

'''
Request Type : POST
endpoint : /payments/transactiondetail
data = {'transactionId':'12345678'}
response : transaction detail, status = 200
'''
class TransactionDetailApi(APIView):
    authentication_classes=[]
    permission_classes = []
    try:
        def post(self,request):
                cookies = request.COOKIES
                response = cookiesAuth(cookies)
                if response:
                    data = request.data
                    transactionDetail = Transaction.objects.get(transactionUrl=data['transactionId'])
                    serializer = TransactionDetailSerializer(transactionDetail)
                    return Response(serializer.data,status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        print(e)

'''
Reqiest Type : GET
endpoint : payments/loandeclinedlist
response : list, status =200
'''
class LoanDeclinedListApi(ListAPIView):
    queryset = Loan.objects.filter(approved=False,declined=True,paid=False)
    authentication_classes = []
    permission_classes = []
    serializer_class = LoanApprovalSerializer
    pagination_class = PageNumberPagination

    try:
        def get(self, request, *args, **kwargs):
            cookies = request.COOKIES
            response = cookiesAuth(cookies)
            if response:
                return self.list(request, *args, **kwargs)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        print(e)

'''
Request Type: GET
endpoint : /payments/loanpaidlist
response : list , status = 200
'''
class LoanPaidListApi(ListAPIView):
    queryset = Loan.objects.filter(approved=True,declined=False,paid=True)
    authentication_classes = []
    permission_classes = []
    serializer_class = LoanApprovalSerializer
    pagination_class = PageNumberPagination

    try:
        def get(self, request, *args, **kwargs):
            cookies = request.COOKIES
            response = cookiesAuth(cookies)
            if response:
                return self.list(request, *args, **kwargs)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        print(e)

'''
Request Type: GET
endpoint : /payments/loannotpaidlist
response : list , status = 200
'''
class LoanNotPaidListApi(ListAPIView):
    queryset = Loan.objects.filter(approved=True,declined=False,paid=False)
    authentication_classes = []
    permission_classes = []
    serializer_class = LoanApprovalSerializer
    pagination_class = PageNumberPagination

    try:
        def get(self, request, *args, **kwargs):
            cookies = request.COOKIES
            response = cookiesAuth(cookies)
            if response:
                return self.list(request, *args, **kwargs)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        print(e)
    
 #Weekly Pools    

#payments/weeklynotpaid
class DifferentiateWeeklyNotPaid(APIView):
    authentication_classes=[]
    permission_classes=[]
    try:
        def post(self,request):
            day = datetime.datetime.today().strftime('%A')
            if True: #Replace true with day == 'Saturday'
                pools = CreatePool.objects.filter(startStatus=True,completeStatus=False, poolType='Weekly')
                for pool in pools:
                    lastDate = datetime.datetime.today()-datetime.timedelta(days=1)
                    if Transaction.objects.filter(poolId = pool, paidTime__date=lastDate).exists(): 
                        paid_users_list = Transaction.objects.filter(poolId = pool, paidTime__date=lastDate).values_list('phone',flat=True)
                        users_list = JoinPool.objects.filter(poolId=pool).values_list('memberId',flat=True)
                        not_paid_users = users_list.difference(paid_users_list)
                        poolId = CreatePool.objects.get(poolId=pool)
                        for phone in not_paid_users:
                            phone = User.objects.get(phone=phone)
                            uniqueId = uniqueIdGenerator()
                            NotPaid.objects.create(poolId=poolId,phone=phone,amount=poolId.contributionAmount,uniqueId = uniqueId)
                    else:
                        continue
                return Response({'message':'Created'},status = status.HTTP_200_OK)
            else:
                return Response({'message':'Request on Saturday'},status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        print(e)

#payments/monthlynotpaid
class DifferentiateMonthlyNotPaid(APIView):
    authentication_classes=[]
    permission_classes=[]
    try:
        def post(self,request):
            day = datetime.datetime.today().strftime('%A') #change day logic for monthly pools
            if day == 'Saturday': # day should be last friday of the month
                pools = CreatePool.objects.filter(startStatus=True,completeStatus=False, poolType='Monthly')
                for pool in pools:
                    lastDate = datetime.datetime.today()-datetime.timedelta(days=1)
                    if Transaction.objects.filter(poolId = pool, paidTime__date=lastDate).exists(): 
                        paid_users_list = Transaction.objects.filter(poolId = pool, paidTime__date=lastDate).values_list('phone',flat=True)
                        users_list = JoinPool.objects.filter(poolId=pool).values_list('memberId',flat=True)
                        not_paid_users = users_list.difference(paid_users_list)
                        poolId = CreatePool.objects.get(poolId=pool)
                        for phone in not_paid_users:
                            phone = User.objects.get(phone=phone)
                            uniqueId = uniqueIdGenerator()
                            NotPaid.objects.create(poolId=poolId,phone=phone,amount=poolId.contributionAmount,uniqueId = uniqueId)
                    else:
                        continue
                return Response({'message':'Created'},status = status.HTTP_200_OK)
            else:
                return Response({'message':'Request on last Saturday of the month'},status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        print(e)

#payments/cronjob
class CronJob(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request):
        try:
            refreshToken()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            print(e)