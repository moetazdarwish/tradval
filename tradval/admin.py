from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(CompanyDetail)
admin.site.register(CompanyEvaluation)
admin.site.register(CompanyReviews)
admin.site.register(CompanyActivity)
admin.site.register(CompanyLookUp)
admin.site.register(EvaluationRequest)
admin.site.register(CompanyClaims)
admin.site.register(UserByUser)
admin.site.register(ContactSupport)