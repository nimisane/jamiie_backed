from django.db import models
from userauth.models import *
# Create your models here.
class CreatePool(models.Model):
    poolId = models.CharField(primary_key=True, unique=True, blank=False, null=False, max_length=255)
    poolOwner = models.ForeignKey(User, related_name='poolowner', on_delete=models.CASCADE)
    poolName = models.CharField(blank=False,null=False,max_length=255)
    contributionAmount = models.IntegerField(null=False)
    deadline = models.DateField()
    poolType = models.CharField(null=False, max_length=255)
    totalMember = models.IntegerField(null=False)
    joinedMember = models.IntegerField(default=0)
    createdAt = models.DateTimeField(auto_now_add=True)
    startStatus = models.BooleanField(default=False)
    completeStatus = models.BooleanField(default=False)

    def __str__(self):
        poolid = self.poolId
        return str(poolid)

class JoinPool(models.Model):
    poolId = models.ForeignKey(CreatePool, related_name='joinedpool', on_delete=models.CASCADE)
    memberId = models.ForeignKey(User, related_name='joinedmember', on_delete=models.CASCADE)
    joinedAt = models.DateTimeField(auto_now_add=True)
    sequence = models.IntegerField(null=False, default=0)
    owner = models.BooleanField(default=False)
    
    def __str__(self):
        memberid = self.memberId
        return str(memberid)

