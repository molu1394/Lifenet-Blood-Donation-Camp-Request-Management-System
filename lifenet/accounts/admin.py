from django.contrib import admin
from .models import *

# Register your models here.
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username","role")
    list_filter = ("role",)
    search_fields = ("role",)

admin.site.register(CustomUser,CustomUserAdmin)