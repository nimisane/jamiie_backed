from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(CustomerUrl)
admin.site.register(Transaction)
admin.site.register(NotPaid)
admin.site.register(LoanDetail)
admin.site.register(Loan)
class ServerStatAdmin(admin.ModelAdmin):
    model = ServerStat
    list_display=['ram','status','timeStamp']
admin.site.register(ServerStat,ServerStatAdmin)