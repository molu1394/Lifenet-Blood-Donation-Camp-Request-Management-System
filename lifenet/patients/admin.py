from django.contrib import admin
from .models import *
# Register your models here.
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ("patient", "donor","status",'blood_group')
    list_filter = ("status",)
    search_fields = ("status",)

admin.site.register(BloodRequest,BloodRequestAdmin)
