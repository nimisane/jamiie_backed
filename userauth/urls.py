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
    path('register',Register.as_view(), name = "register"),
    path('login',Login.as_view(), name = "login"),
    path('phone',Phone.as_view(), name="phone verification"),
    path('phoneverification', PhoneVerification.as_view(), name="phone verification"),
    path('resendotp',ResendOtp.as_view(),name = "resend otp"),
    path('forgotpassword',ForgotPassword.as_view(), name = "forgot password"),
    path('forgotpassword/<int:id>/',ForgotPassword.as_view(), name = "forgot password id"),
    path('logout', Logout.as_view(), name="logout"),
    path('adminlogin',AdminLogin.as_view(), name="admin login"),
    path('adminlogout',AdminLogout.as_view(), name="admin logout"),
    path('riskscore',ScoreCalculator.as_view(), name="score calculator"),
    path('check',Check.as_view(), name = "check"),
    path('completeprofile',CompleteProfileApi.as_view(), name="complete profile"),
    path('getuserdetail/<int:id>/',SingleUserDetailApi.as_view(), name = "get user api"),
    path('singleuserdetail/<int:id>/',AdminSingleUserDetailApi.as_view(), name="admin single user"),
    path('usersdetail',UsersDetailApi.as_view(), name = 'users detail'),
    path('document',UploadDocumentApi.as_view(),name='upload document'),
    path('sociallogin',SocialLoginApi.as_view(),name='social login'),
    path('socialregister',SocialRegister.as_view(),name='social register'),
]