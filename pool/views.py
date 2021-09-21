from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework import status
from .models import *
import hashlib
import time
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import *
import json
from rest_framework.pagination import PageNumberPagination
from rest_framework.authtoken.models import Token
import requests
from django.core.paginator import Paginator
from payments.models import *
from django.db.models import Sum
from payments.serializers import *
from datetime import date
"""
Create your views here.
"""
def uniqueid():
    milli_sec = str(round(time.time() * 1000))
    hashed_val = hashlib.sha256(milli_sec.encode())
    milli_sec  = hashed_val.hexdigest()
    value = str(milli_sec[:8])
    return value

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

def notification(mobileId, message):
    URL = "https://fcm.googleapis.com/fcm/send"
    FIREBASE_KEY = 'AAAAfXag7NM:APA91bEogzEjU5msPgxNW8qd-Ih6DJeN6uQDpdchHfnETdGKJ6diMn2jA8pXdNuJA97Jqvv8Y-TDd5QfyWmNiXkxFLLx7PrnI6mHHLTM0BgQcqPq8sE87JHz0CqzJPo4N4RBYjJogBzw'
    CONTENT_TYPE = 'application/json'
    HEADERS = {
      "Content-Type": CONTENT_TYPE,
       "Authorization": 'key='+FIREBASE_KEY
    }
    PARAMS = {
      "notification": {
          "body": message,
          "title": "Notification"
      },
      "priority": "high",
       "data": {
           "click_action": "FLUTTER_NOTIFICATION_CLICK",
           "id": "1",
           "status": "done"
      },
      "to": mobileId
    }
    r = requests.post(URL, data=json.dumps(PARAMS), headers=HEADERS)
    print("notification Response",r)
    return True

class CreatePoolApi(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes=[IsAuthenticated] 
    def post(self,request):
        try:
            data = request.data
            poolOwner = data['poolOwner']
            poolName =  data['poolName']
            contributionAmount = data['contributionAmount']
            deadline = data['deadline']
            poolType = data['poolType']
            totalMember = data['totalMember']
            poolOwner = User.objects.get(phone = poolOwner)
            poolId = uniqueid()
            obj = CreatePool.objects.create(poolId=poolId, poolOwner = poolOwner, poolName = poolName, contributionAmount = contributionAmount, deadline = deadline, poolType = poolType, totalMember=totalMember)
            JoinPool.objects.create(poolId=obj, memberId=poolOwner, owner=True)
            obj.joinedMember = obj.joinedMember+1
            obj.save()
            return Response({'poolId':poolId},status=status.HTTP_200_OK)
        except Exception as e:
            print(e)

class JoinPoolApi(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            data = request.data
            poolId = data['poolId']
            memberId = data['memberId']
            if CreatePool.objects.filter(poolId=poolId).exists() and User.objects.filter(phone=memberId).exists():
                pool = CreatePool.objects.get(poolId=poolId)
                if pool.deadline >= date.today():
                    member = User.objects.get(phone=memberId)
                    if JoinPool.objects.filter(poolId=poolId, memberId=member):
                        return Response({'response':'User already joined'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
                    elif pool.totalMember == pool.joinedMember:
                        return Response({'response':'pool filled'},status=status.HTTP_401_UNAUTHORIZED)   
                    else:
                        create_member = JoinPool.objects.create(poolId=pool, memberId=member)
                        pool.joinedMember = pool.joinedMember + 1 
                        pool.save()
                        return Response({'poolId':pool.poolId},status=status.HTTP_200_OK)
                else:
                    return Response({'response':'Join date is expired'},status = status.HTTP_406_NOT_ACCEPTABLE)
            else:
                return Response({'response':'Pool Id is wrong'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        except Exception as e:
            print(e)   

class SearchPoolApi(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            data = request.data
            poolId = data['poolId']
            if CreatePool.objects.filter(poolId=poolId).exists():
                pool = CreatePool.objects.get(poolId=poolId)
                phone = pool.poolOwner
                poolOwner = User.objects.get(phone=phone)
                return_response = {'poolId':pool.poolId,'poolName':pool.poolName,'poolOwner':poolOwner.phone,'contributionAmount':pool.contributionAmount,'totalMember':pool.totalMember,'joinedMember':pool.joinedMember,'deadline':pool.deadline}
                return Response(return_response, status=status.HTTP_200_OK)
            else:
                return Response({'response':'Pool does not exists'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)

class CreatePoolDetailApi(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self,request,id):
        poolOwner = "+"+str(id)
        poolDetail = CreatePool.objects.filter(poolOwner=poolOwner)
        serializer = CreatePoolDetailSerializer(poolDetail, many=True)
        response = serializer.data
        return Response({'poolDetails':response},status=status.HTTP_200_OK)

class PoolUsersDetailApi(APIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = [IsAuthenticated,]
    def get(self,request,id):
        queryset = JoinPool.objects.filter(poolId=id)
        serializer = PoolUsersDetailSerializer(queryset, many=True)
        return Response(serializer.data)

class PoolDetailsAdminApi(ListAPIView):
    queryset = CreatePool.objects.all()
    authentication_classes = []
    permission_classes = []
    serializer_class = CreatePoolDetailSerializer
    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        cookies = request.COOKIES
        response = cookiesAuth(cookies)
        if response:
            return self.list(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

class PoolDetailApi(APIView):
    authentication_classes = []
    permission_classes = []
    try:
        def get(self,request,id):
            cookies = request.COOKIES
            if cookiesAuth(cookies):
                pool = CreatePool.objects.get(poolId = id)
                serializer = CreatePoolDetailSerializer(pool)
                return Response(serializer.data,status = status.HTTP_200_OK)
            
            else:
                return Response(status = status.HTTP_401_UNAUTHORIZED)
    
    except Exception as e:
        print(e)

class SinglePoolDetailApi(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  
    try:
        def get(self,request,id):  
            queryset = CreatePool.objects.get(poolId=id)
            serializer = SinglePoolDetailApiSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)

class AdminSinglePoolDetailApi(APIView):
    authentication_classes=[]
    permission_classes=[]
    try:
        def get(self,request,id):
            cookies = request.COOKIES
            if cookiesAuth(cookies):  
                queryset = CreatePool.objects.get(poolId=id)
                serializer = SinglePoolDetailApiSerializer(queryset)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        print(e)

class NotificationApi(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self,request):
        data = request.data
        phone = data['phone']
        mobileId = Notification.objects.get(phone=phone).mobileId
        response = notification(mobileId)
        return Response(status=status.HTTP_201_CREATED)

class StartPoolApi(APIView):
    authentication_classes=[TokenAuthentication,]
    permission_classes=[IsAuthenticated,]

    try:
        def post(self,request):
            data = request.data
            poolId = data['poolId']
            message = 'Pool '+poolId+' is started'
            pool = CreatePool.objects.get(poolId=poolId)
            if pool.joinedMember == pool.totalMember:    
                for i in range(1,pool.totalMember+1):
                    phone = data['sequenceDetail'][i]['phone']
                    user = JoinPool.objects.get(poolId = poolId,memberId = phone)
                    user.sequence = data['sequenceDetail'][i]['sequence']
                    user.save()
                    if Notification.objects.filter(phone = phone).exists():
                        mobileId = Notification.objects.get(phone = phone).mobileId
                        notification(mobileId,str(message))
                    else:
                        continue
                pool.startStatus = True
                pool.save()    
                return Response({'response':'Pool is started'},status=status.HTTP_200_OK)
            else:
                return Response({'response':'Joined members are not equal to total members'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    except Exception as e:
        print(e)

class DashboardApi(APIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = [IsAuthenticated,]
    try:
        def get(self,request,id):
            phone = '+'+str(id)
            image = "https://jamiie-user-images.s3.amazonaws.com/ProfileImages/"+str(id)+".jpg"
            userName = User.objects.get(phone=phone).name
            createdPools = CreatePool.objects.filter(poolOwner = phone).count()
            joinedPools = JoinPool.objects.filter(memberId = phone).count()
            completedPools = CreatePool.objects.filter(poolOwner = phone, completeStatus = True).count()
            if Transaction.objects.filter(phone=phone).exists():
                transactionDetail = Transaction.objects.filter(phone=phone, transactionStatus=True)
                moneySaved = transactionDetail.aggregate(totalAmount=Sum('amount'))
                transactions = PaidDetailSerializer(transactionDetail[:2], many=True)
                upcomingPayments =  [
                                        {
                                        "id": "1",
                                        "name": "Pool 1",
                                        "date": "25-08-2020",
                                        "amount": "750"
                                        }
                                    ]
                return_response = {'response':True,'name':userName,'image':image,'createdPools':createdPools,'joinedPools':joinedPools,'completedPools':completedPools,'moneySaved':moneySaved['totalAmount'], 'transactions':transactions.data,'upcomingPayments':upcomingPayments}
                return Response(return_response,status = status.HTTP_200_OK)
            else:
                return Response({'response':False, 'name':userName,'image':image, 'createdPools':createdPools,'joinedPools':joinedPools,'completedPools':completedPools,'moneySaved':0, 'transactions':'No transaction yet','upcomingPayments':'No upcoming payment yet'},status=status.HTTP_200_OK)

    except Exception as e:
        print(e)

class Testing(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self,request):
        pool = CreatePool.objects.all()
        paginator = Paginator(pool, 1)
        page = request.GET.get('page', 1)
        users = paginator.page(page)
        return Response({'user':users})

class UserJoinedPoolApi(APIView):
    try:
        authentication_classes=[TokenAuthentication,]
        permission_classes=[IsAuthenticated,]
        def get(self,request,id):
            phone = "+"+str(id)
            joinedPool = JoinPool.objects.filter(memberId=phone, owner=False)
            serializer = PoolUsersDetailSerializer(joinedPool,many=True)
            return Response({'response':serializer.data},status=status.HTTP_200_OK)

    except Exception as e:
        print(e)