from django.contrib import admin
from .models import Request

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'status', 'created_at')
    search_fields = ('customer_name',)