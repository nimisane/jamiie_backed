from django.contrib import admin
from .models import *
# Register your models here.
class JoinPoolModel(admin.ModelAdmin):
    model = JoinPool
    list_display = ['poolid','memberid','joinedat']
admin.site.register(CreatePool)
admin.site.register(JoinPool)