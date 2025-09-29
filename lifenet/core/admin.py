from django.contrib import admin
from .models import ContactQuery

@admin.register(ContactQuery)
class ContactQueryAdmin(admin.ModelAdmin):
    list_display = ("firstname", "lastname", "email", "subject", "created_at", "is_resolved")
    list_filter = ("is_resolved", "created_at")
    search_fields = ("firstname", "lastname", "email", "subject", "message")
    list_editable = ("is_resolved",)