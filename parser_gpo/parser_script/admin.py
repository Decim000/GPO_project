from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from django.contrib.auth.admin import UserAdmin
from accounts.models import CustomUser, Profile
# Register your models here.


admin.site.register(Report)

admin.site.register(FederalLaw)

admin.site.register(Technology)

admin.site.register(PurchaseStage)

admin.site.register(Tender)

admin.site.register(KeyWords)

admin.site.register(SupplierDefinition)

admin.site.register(TenderDocument)


class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'is_staff',
        'company_name'
    )

    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Additional info', {
            'fields': ('company_name', )
        })
    )

    add_fieldsets = (
        (None, {
            'fields': ('username', 'password1', 'password2')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Additional info', {
            'fields': ('company_name', )
        })
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile)
