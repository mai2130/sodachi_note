from django.contrib import admin
from .models import Child

@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ("id", "name", 'nursery', 'classroom', 'withdrawn_month', 'created_at')
    list_filter = ('nursery', 'classroom', 'withdrawn_month')    
    search_fields = ("name",)
    ordering = ('name',)
