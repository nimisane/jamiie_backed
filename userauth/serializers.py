from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate
from rest_framework import exceptions
from djoser.serializers import UserCreateSerializer, UserSerializer


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('phone','password','email','name',)

    def create(self,validated_data):
        user = super(RegisterSerializer,self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ('phone','jobAge','family','poolingRecord','savingReason','riskScore','riskBand',)

class UsersDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('image','phone','name','email','createdAt','lastLogin',)

class UsersDetailPoolSerializer(serializers.ModelSerializer):
    riskStatus = UserInfoSerializer(many=True)
    class Meta:
        model = User
        fields = ('image','phone','name','riskStatus',)
