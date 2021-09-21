from django.contrib import admin
from .models import *

# Register your models here.
class UserModel(admin.ModelAdmin):
    model = User
    list_display = ['phone','email','name','createdAt','lastLogin']
admin.site.register(User, UserModel)
admin.site.register(OTP)
admin.site.register(RiskCondition)
admin.site.register(UserInfo)
admin.site.register(Notification)
admin.site.register(SocialLogin)