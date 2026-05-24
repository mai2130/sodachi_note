from django.contrib import admin
from .models import Nursery, Classroom

@admin.register(Nursery)
class NurseryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name','user')
    
@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')   
    search_fields = ('name',) 