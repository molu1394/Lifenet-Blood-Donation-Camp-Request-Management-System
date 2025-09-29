from django.contrib import admin
from .models import *

# Register your models here.
class CampAdmin(admin.ModelAdmin):
    list_display = ("name", "city","start_time","end_time")
    list_filter = ("city",)
    search_fields = ("city",)

class CampSlotAdmin(admin.ModelAdmin):
    list_display = ("camp", "start_time","end_time","capacity")
    list_filter = ("booked_count",)
    search_fields = ("camp",)

class CampAppointmentAdmin(admin.ModelAdmin):
    list_display = ("camp", "slot","status")
    list_filter = ("status",)
    search_fields = ("camp",)

admin.site.register(Camp,CampAdmin)
admin.site.register(CampSlot,CampSlotAdmin)
admin.site.register(CampAppointment,CampAppointmentAdmin)
