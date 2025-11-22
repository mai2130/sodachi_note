from django.contrib import admin
from .models import Nursery, Classroom

@admin.register(Nursery)
class NurseryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    
@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'nursery','created_at')   
    list_filter = ('nursery',)  
    search_fields = ('name',) 