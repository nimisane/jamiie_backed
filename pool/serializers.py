from rest_framework import serializers
from .models import *
from userauth.models import *
from userauth.serializers import *
#create your serializers here 
class CreatePoolDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreatePool
        fields = ('poolId','poolName','contributionAmount','joinedMember','poolType','totalMember','createdAt','startStatus',)

class PoolUsersDetailSerializer(serializers.ModelSerializer):
    poolId = CreatePoolDetailSerializer()
    class Meta:
        model = JoinPool
        fields = '__all__'

class JoinPoolSerializer(serializers.ModelSerializer):
    memberId = UsersDetailPoolSerializer()
    class Meta:
        model = JoinPool
        fields = '__all__'

class SinglePoolDetailApiSerializer(serializers.ModelSerializer):
    joinedpool = JoinPoolSerializer(many=True)
    class Meta:
        model = CreatePool
        fields = ('poolId','poolOwner','poolName','contributionAmount','joinedMember','poolType','totalMember','createdAt','deadline','joinedpool','startStatus','completeStatus',)