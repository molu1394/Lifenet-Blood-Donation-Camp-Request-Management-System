from django.contrib import admin
from .models import *

# Register your models here.
class CampInventoryAdmin(admin.ModelAdmin):
    list_display = ('camp','blood_group','units_collected')
    list_filter = ("camp",)
    search_fields = ("blood_group",)

class BloodBankInventoryAdmin(admin.ModelAdmin):
    list_display = ('bloodbank','blood_group','units_available')
    list_filter = ("bloodbank",)
    search_fields = ("blood_group",)

admin.site.register(CampInventory,CampInventoryAdmin)
admin.site.register(BloodBankInventory,BloodBankInventoryAdmin)