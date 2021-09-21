from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
import random
import boto3
from twilio.rest import Client
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from .models import *
from pool.models import *
from pool.serializers import *
#Create your views here.
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.hashers import check_password
from django.http import HttpResponse
import json
from dotenv import load_dotenv
from pathlib import Path
import os
import datetime
env_file = Path('.') / '.env'
load_dotenv(dotenv_path=env_file)   
from payments.utilFunctions import *
from payments.models import *


#OTP GENERATOR
def otpGenerator():
    otp = random.randrange(10000,100000)
    return otp

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

def ageCalculator(DOB):
    birthYear = int(DOB.year)
    currentYear = datetime.datetime.now()
    age = int(currentYear.year) - birthYear
    return age 

def twilioService(phone,otp):
    account_sid = os.getenv('ACCOUNT_SID')
    auth_token = os.getenv('AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    message = client.messages \
    .create(
    body="Your otp number is "+str(otp),
    from_=os.getenv('FROM_NUMBER'),
    to=str(phone)
    )
    print(message.sid)
    return Response(status=status.HTTP_201_CREATED)

class Phone(APIView):
    authentication_classes = []
    permission_classes=[] 
    def post(self,request):
        try:
            data = request.data
            phone = data["phone"]
            if OTP.objects.filter(phone=phone).exists():
                user_instance = OTP.objects.get(phone=phone)
                if user_instance.validated == True and user_instance.register==True:
                    return Response({'response':'User already exists'},status = status.HTTP_409_CONFLICT)
                else:
                    otp = otpGenerator()
                    user_instance.otp = otp
                    user_instance.save()
                    response = twilioService(phone,otp)
                    return response
            else:
                otp = otpGenerator()
                OTP.objects.create(phone=phone, otp = otp, validated=False)
                '''
                Otp service created here using AWS SNS
                +12185204544
                '''
                response = twilioService(phone,otp)
                return response
        except Exception as e:
            print(e)       

class PhoneVerification(APIView):
    authentication_classes = []
    permission_classes=[] 
    try:
        def post(self,request):
            data = request.data
            phone = data["phone"]
            otp = data["otp"]
            user = OTP.objects.get(phone=phone)
            if user.otp == otp:
                user.validated=True
                user.save()
                return Response(status = status.HTTP_201_CREATED)
            else:
                return Response ({'response':'Invalid authorization code'},status = status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)

class ResendOtp(APIView):  
    authentication_classes = []
    permission_classes=[]  
    try:
        def post(self,request):
            data = request.data
            phone = data["phone"]
            user_instance = OTP.objects.get(phone=phone)
            if user_instance.validated == False:
                otp = otpGenerator()
                user_instance.otp = otp
                user_instance.save()
                response = twilioService(phone,otp)
                return response
            else: 
                return Response(status=status.HTTP_302_FOUND)
    except Exception as e:
        print(e)

class Register(APIView):
    authentication_classes = []
    permission_classes=[] 
    def post(self,request):
        try:
            data = request.data
            phone = data['phone']
            serializer = RegisterSerializer(data=data)
            if serializer.is_valid():
                user = OTP.objects.get(phone=phone)
                user.register = True
                user.save()
                serializer.save()
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response({'message':'Enter valid credentials'},status=status.HTTP_406_NOT_ACCEPTABLE)
        except Exception as e:
            print(e)

class Login(APIView):
    authentication_classes = []
    permission_classes=[] 
    def post(self,request):
        try:
            value = request.data
            phone  = value["phone"]
            password = value["password"]
            mobileId = value["mobileId"]
            if User.objects.filter(phone = phone).exists():
                user = User.objects.get(phone = phone)
                if user is not None:    
                    valid_password = check_password(password,user.password)
                    if valid_password==True:
                        token, created = Token.objects.get_or_create(user=user)
                        user.save()
                        completeProfile = User.objects.get(phone=phone).completeProfile
                        bankAdded = User.objects.get(phone=phone).bankAdded
                        riskCalculator = UserInfo.objects.filter(phone=phone).exists()
                        if Notification.objects.filter(phone=phone).exists():
                            if str(Notification.objects.get(phone=phone).mobileId) == str(mobileId):
                                return Response({'token': token.key,'completeProfile':completeProfile,'riskCalculator':riskCalculator,'bankAdded':bankAdded},status=status.HTTP_200_OK)
                            else:
                                notificationObject = Notification.objects.get(phone=user)
                                notificationObject.mobileId = mobileId
                                notificationObject.save()
                                return Response({'token': token.key,'completeProfile':completeProfile,'riskCalculator':riskCalculator,'bankAdded':bankAdded},status=status.HTTP_200_OK)
                        else:
                            notificationObject = Notification.objects.create(phone=user,mobileId=mobileId)
                            return Response({'token': token.key,'completeProfile':completeProfile,'riskCalculator':riskCalculator,'bankAdded':bankAdded},status=status.HTTP_200_OK)
                    else:
                        return Response({'response':'Wrong Credentials'},status=status.HTTP_401_UNAUTHORIZED)
                else:
                    return Response(status=status.HTTP_404_NOT_FOUND)        
            else:
                return Response({'response':'User does not exists'},status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            print(e)

class CompleteProfileApi(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes=[IsAuthenticated]
    try:
        def post(self,request):
            data = request.data
            phone = data['phone']
            user = User.objects.get(phone=phone)
            user.image = data['image']
            user.street = data['street']
            user.city = data['city']
            user.state = data['state']
            user.zipCode = data['zipCode']
            user.addressAge = data['addressAge']
            user.DOB = data['DOB']
            user.securityNumber = data['securityNumber']
            if User.objects.filter(securityNumber=user.securityNumber).exists():
                return Response({'response':'This Security Number already used'},status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                user.employerName = data['employerName']
                user.employerAge = data['employerAge']
                name = user.name.split()
                firstName = name[0]
                lastName = name[1]
                dwollaState = data['state'] 
                stateCode={
                            'Alabama': 'AL',
                            'Alaska': 'AK',
                            'Arizona': 'AZ',
                            'Arkansas': 'AR',
                            'California': 'CA',
                            'Colorado': 'CO',
                            'Connecticut': 'CT',
                            'Delaware': 'DE',
                            'Florida': 'FL',
                            'Georgia': 'GA',
                            'Hawaii': 'HI',
                            'Idaho': 'ID',
                            'Illinois': 'IL',
                            'Indiana': 'IN',
                            'Iowa': 'IA',
                            'Kansas': 'KS',
                            'Kentucky': 'KY',
                            'Louisiana': 'LA',
                            'Maine': 'ME',
                            'Maryland': 'MD',
                            'Massachusetts': 'MA',
                            'Michigan': 'MI',
                            'Minnesota': 'MN',
                            'Mississippi':'MS',
                            'Missouri':'MO',
                            'Montana': 'MT',
                            'Nebraska': 'NE',
                            'Nevada': 'NV',
                            'New Hampshire':'NH',
                            'New Jersey': 'NJ',
                            'New Mexico': 'NM',
                            'New York': 'NY',
                            'North Carolina': 'NC',
                            'North Dakota': 'ND',
                            'Ohio': 'OH',
                            'Oklahoma': 'OK',
                            'Oregon': 'OR',
                            'Pennsylvania': 'PA',
                            'Rhode Island': 'RI',
                            'South Carolina': 'SC',
                            'South Dakota': 'SD',
                            'Tennessee': 'TN',
                            'Texas': 'TX',
                            'Utah': 'UT',
                            'Vermont': 'VT',
                            'Virginia': 'VA',
                            'Washington': 'WA',
                            'West Virginia': 'WV',
                            'Wisconsin': 'WI',
                            'Wyoming': 'WY',
                        }
                dwolla_create_user = {'firstName':firstName, 'lastName':lastName,'email':user.email,'address1':data['street'],'city':data['city'],'state':stateCode[dwollaState],'postalCode':data['zipCode'],'dateOfBirth':data['DOB'],'ssn':data['securityNumber'],'type':'personal'}
                customer_url = create_customer(dwolla_create_user)
                if customer_url == 400:
                    user.completeProfile = True
                    user.save()
                    return Response({'response':'Your dwolla bank is already exist'},status = status.HTTP_201_CREATED)
                elif customer_url != 400:
                    CustomerUrl.objects.create(phone = user, customerUrl = customer_url)
                    user.completeProfile = True
                    user.save()
                    return Response(status = status.HTTP_201_CREATED)
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print(e)

class ForgotPassword(APIView):
    authentication_classes = []
    permission_classes=[]
    def post(self,request):
        try:
            data = request.data
            phone = data["phone"]
            if User.objects.filter(phone=phone).exists():
                user = OTP.objects.get(phone=phone)
                otp = otpGenerator()
                user.otp = otp
                user.save()
                response = twilioService(phone,otp)
                return response
            else:
                return Response({'response':'User does not exists'},status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            print(e)        

    def put(self,request,id):
        try:
            data = request.data
            phone = "+"+str(id)
            password = data["password"]
            user = User.objects.get(phone=phone)
            user.set_password(password)
            user.save()
            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)

class Logout(APIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes=[IsAuthenticated,]
    def post(self, request):
        try:
            data = request.data
            phone = data["phone"]
            user = User.objects.get(phone=phone) 
            Token.objects.filter(user=user).delete()
            Notification.objects.filter(phone=phone).delete()
            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)

class AdminLogin(APIView):
    authentication_classes = []
    permission_classes=[] 
    def post(self,request):
        try:
            value = request.data
            phone  = value["phone"]
            password = value["password"]
            user = User.objects.get(phone = phone)
            if user is not None:
                valid_password = check_password(password,user.password)
                if valid_password==True:
                    token, created = Token.objects.get_or_create(user=user)
                    totalUsers = User.objects.filter(admin=False).count()
                    totalPools = CreatePool.objects.all().count()
                    completedPools = CreatePool.objects.filter(completeStatus=True).count()
                    totalTransactions = Transaction.objects.all().count()
                    totalLoans = Loan.objects.all().count()
                    totalApprovedLoans = Loan.objects.filter(approved =True).count()
                    totalDeclinedLoans = Loan.objects.filter(declined = True).count()
                    return_data = {'name':user.name,'phone':user.phone,'email':user.email,'totalTransactions':totalTransactions,'totalUsers':totalUsers,'totalPools':totalPools,'completedPools':completedPools, 'totalLoans':totalLoans,'totalApprovedLoans':totalApprovedLoans,'totalDeclinedLoans':totalDeclinedLoans}
                    user.save()
                    response = HttpResponse(json.dumps(return_data),status=status.HTTP_200_OK)
                    response.set_cookie(phone, value = token, max_age=None, expires=None, path='/', domain=None, secure=True, httponly=True, samesite='none')
                    return response
                else:
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)

class AdminLogout(APIView):
    authentication_classes = []
    permission_classes=[] 
    def post(self, request):
        try:
            val = request.COOKIES
            print("cookies=",val)
            count = 0
            for i in val:
                count=count+1
                if (count == 1):
                    user = User.objects.get(phone = i)
                    if Token.objects.filter(user=user).exists():
                        user_token = Token.objects.get(user=user)
                        user_cookies = request.COOKIES[i]
                        if str(user_token) == str(user_cookies):
                            user_token.delete()
                            response = HttpResponse(status = status.HTTP_200_OK)
                            response.delete_cookie(i)
                            return response
                        else:
                            return HttpResponse(status = status.HTTP_401_UNAUTHORIZED)
                    else:
                        return HttpResponse(status = status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print(e)    

class Check(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self,request):
        try:
            val = request.COOKIES
            count = 0
            for i in val:
                count=count+1
                if (count == 1):
                    user = User.objects.get(phone = i)
                    if Token.objects.filter(user=user).exists():
                        if str(Token.objects.get(user=user)) == str(request.COOKIES[i]):
                            totalUsers = User.objects.filter(admin=False).count()
                            totalPools = CreatePool.objects.all().count()
                            completedPools = CreatePool.objects.filter(completeStatus=True).count()
                            totalTransactions = Transaction.objects.all().count()
                            totalLoans = Loan.objects.all().count()
                            totalApprovedLoans = Loan.objects.filter(approved =True).count()
                            totalDeclinedLoans = Loan.objects.filter(declined = True).count()
                            return_data = {'name':user.name,'phone':user.phone,'email':user.email,'totalTransactions':totalTransactions,'totalUsers':totalUsers,'totalPools':totalPools,'completedPools':completedPools, 'totalLoans':totalLoans,'totalApprovedLoans':totalApprovedLoans,'totalDeclinedLoans':totalDeclinedLoans}
                            return HttpResponse(json.dumps(return_data),status = status.HTTP_200_OK)
                        else:
                            return HttpResponse(status = status.HTTP_401_UNAUTHORIZED)
                    else:
                        return HttpResponse(status = status.HTTP_401_UNAUTHORIZED)                  
        except Exception as e:
            print(e)

class ScoreCalculator(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            data  = request.data
            phone = data['phone']
            jobAge = data['jobAge']
            family = data['family']
            DOB = User.objects.get(phone = phone).DOB
            age = ageCalculator(DOB)
            if age < 20:
                age = "<20 years"
            elif age < 25:
                age = "<25 years"
            elif age < 30:
                age = "<30 years"
            else:
                age = ">35 years"
            poolingRecord = data['poolingRecord']
            repaymentRecord = 0
            living = int(User.objects.get(phone = phone).addressAge)
            if living == 1:
                living = "1"
            elif living == 2:
                living = "2"
            elif living == 3:
                living = "3"
            else:
                living = ">3"
            jobAge = RiskCondition.objects.get(jobAge=jobAge)
            family = RiskCondition.objects.get(family=family)
            age = RiskCondition.objects.get(age=age)
            savingMoney = RiskCondition.objects.get(poolingRecord=poolingRecord)
            loans = RiskCondition.objects.get(repaymentRecord = repaymentRecord)
            living = RiskCondition.objects.get(living=living)
            riskScore =12 + jobAge.score + family.score + age.score + savingMoney.score + loans.score + living.score
            serializer = UserInfoSerializer(data = data)
            if serializer.is_valid():
                    serializer.save()
                    user = UserInfo.objects.get(phone=phone)
                    user.riskScore = riskScore
                    if riskScore >=21 and riskScore<=50:
                        user.riskBand = 'Risky'
                    elif riskScore >=51 and riskScore<=70:
                        user.riskBand = 'Moderate'
                    else:
                        user.riskBand = 'Low'
                    user.save()
                    return Response(status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        except Exception as e:
            print(e)          

class SingleUserDetailApi(APIView):
    authentication_classes = [TokenAuthentication,]
    permission_classes = [IsAuthenticated,]
    try:
        def get(self,request,id):
            phone = "+"+str(id)
            image = "https://jamiie-user-images.s3.amazonaws.com/ProfileImages/"+str(id)+".jpg"
            user = User.objects.get(phone=phone)
            return_response={'phone':user.phone,'name':user.name,'image':image,'email':user.email,'state':user.state,'city':user.city,'createdAt':user.createdAt,'lastLogin':user.lastLogin,'DOB':user.DOB}
            return Response(return_response)

    except Exception as e:
        print(e)

class UsersDetailApi(ListAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = User.objects.filter(admin=False,staff=False)
    serializer_class = UsersDetailSerializer
    pagination_class = PageNumberPagination


    def get(self, request, *args, **kwargs):
        cookies = request.COOKIES
        response = cookiesAuth(cookies)
        if response:
            return self.list(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

class AdminSingleUserDetailApi(APIView):
    authentication_classes = []
    permission_classes = []
    try:
        def get(self,request,id):
            cookies = request.COOKIES
            response = cookiesAuth(cookies)
            if response:
                phone = "+"+str(id)
                image = "https://jamiie-user-images.s3.amazonaws.com/ProfileImages/"+str(id)+".jpg"
                user = User.objects.get(phone=phone)
                userinfo = UserInfo.objects.get(phone = phone)
                joinedPool = JoinPool.objects.filter(memberId=phone, owner=False)
                serializerJoinedPool = PoolUsersDetailSerializer(joinedPool, many=True)
                createdPool = CreatePool.objects.filter(poolOwner=phone)
                serializerCreatedPool = CreatePoolDetailSerializer(createdPool, many = True)
                return_response={'phone':user.phone,'name':user.name,'image':image,'email':user.email,'state':user.state,'city':user.city,'createdAt':user.createdAt,'lastLogin':user.lastLogin,'DOB':user.DOB,'riskScore':userinfo.riskScore,'jobAge':userinfo.jobAge,'family':userinfo.family,'poolingRecord':userinfo.poolingRecord,'repaymentRecord':userinfo.repaymentRecord,'riskBand':userinfo.riskBand,'savingReason':userinfo.savingReason, 'joinedPool':serializerJoinedPool.data,'createdPool':serializerCreatedPool.data}
                return Response(return_response)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        print(e)

class UploadDocumentApi(APIView):
    authentication_classes=[]
    permission_classes=[]
    try:
        def post(self,request):
            data = request.dataḍ
            phone=data['phone']
            documentType = data['documentType']
            user = CustomerUrl.objects.get(phone=phone)
            user.document = data['document']
            user.documentType = documentType
            user.save()
            documentImageUrl = "https://jamiie-user-images.s3.amazonaws.com/DocumentImages/"+phone[1:]+".jpg"
            customer_url = user.customerUrl
            documenturl = upload_customer_documents(customer_url,documentImageUrl,documentType)
            user.documentUrl = documenturl
            user.save()
            return Response(status = status.HTTP_201_CREATED)

    except Exception as e:
        print(e)

#sociallogin
class SocialLoginApi(APIView):
    authentication_classes=[]
    permission_classes=[]
    try:
        def post(self,request):
            data = request.data
            email = data['email'] 
            if SocialLogin.objects.filter(email=email).exists():
                if SocialLogin.objects.get(email=email).firstLogin:
                    mobileId=data['mobileId']
                    user = User.objects.get(email=email)
                    phone = user.phone
                    token, created = Token.objects.get_or_create(user=user)
                    completeProfile = User.objects.get(phone=phone).completeProfile
                    riskCalculator = UserInfo.objects.filter(phone=phone).exists()
                    if Notification.objects.filter(phone=phone).exists():
                        if str(Notification.objects.get(phone=phone).mobileId) == str(mobileId):
                            return Response({'firstLogin':True,'token': token.key,'completeProfile':completeProfile,'riskCalculator':riskCalculator,'phone':phone},status=status.HTTP_200_OK)
                        else:
                            notificationObject = Notification.objects.get(phone=user)
                            notificationObject.mobileId = mobileId
                            notificationObject.save()
                            return Response({'firstLogin':True,'token': token.key,'completeProfile':completeProfile,'riskCalculator':riskCalculator,'phone':phone},status=status.HTTP_200_OK)
                    else:
                        notificationObject = Notification.objects.create(phone=user,mobileId=mobileId)
                        return Response({'firstLogin':True,'token': token.key,'completeProfile':completeProfile,'riskCalculator':riskCalculator,'phone':phone},status=status.HTTP_200_OK)
                else:
                    return Response({'firstLogin':False},status=status.HTTP_200_OK)
            else:
                SocialLogin.objects.create(email=email)
                return Response({'firstLogin':False},status=status.HTTP_200_OK)
    except Exception as e:
        print(e)

#socialregister
class SocialRegister(APIView):
    authentication_classes = []
    permission_classes=[] 
    def post(self,request):
        try:
            data = request.data
            phone = data['phone']
            email = data['email']
            name = data['name']
            User.objects.create(phone=phone,email=email,name=name)
            user = OTP.objects.get(phone=phone)
            user.register = True
            user.save()
            social = SocialLogin.objects.get(email=email)
            social.firstLogin =True
            social.save()
            return Response(status=status.HTTP_201_CREATED)                
        except Exception as e:
            print(e)