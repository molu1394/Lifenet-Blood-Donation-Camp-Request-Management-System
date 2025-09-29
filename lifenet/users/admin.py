from django.contrib import admin
from .models import *

# Register your models here.
class DonorProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "blood_group", "ready_to_donate", "address","age"]
    list_filter = ("blood_group", "ready_to_donate")
    readonly_fields = ("age",)
    search_fields = ("user__username", "location")

class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "blood_group_req","address")
    list_filter = ("blood_group_req","address")
    search_fields = ("user__username", "adress")


class BloodBankProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "bloodbank_name","approval_status")
    list_filter = ("address",)
    search_fields = ("user__username", "adress")

class OrganizationProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "organization_name","approval_status")
    list_filter = ("organization_type",)
    search_fields = ("user__username",)


class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "bloodbank_name","approval_status")
    list_filter = ("bloodbank_name",)
    search_fields = ("user__username", "bloodbank_name")


class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)
    
admin.site.register(DonorProfile, DonorProfileAdmin)
admin.site.register(PatientProfile,PatientProfileAdmin)
admin.site.register(BloodBankProfile, BloodBankProfileAdmin)
admin.site.register(OrganizationProfile,OrganizationProfileAdmin)
admin.site.register(StaffProfile, StaffProfileAdmin)
admin.site.register(AdminProfile, AdminProfileAdmin)