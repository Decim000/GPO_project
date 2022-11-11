from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Register your models here.


admin.site.register(Report)

admin.site.register(FederalLaw)

admin.site.register(Technology)

admin.site.register(PurchaseStage)

admin.site.register(Tender)