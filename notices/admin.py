from django.contrib import admin
from .models import Notice,NoticeClassroom

class NoticeClassroomInline(admin.TabularInline):
    model = NoticeClassroom
    extra = 1 # 空行を1行表示

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'date' ,'nursery', 'created_at')
    list_filter = ('category', 'date', 'nursery')
    search_fields =('title','body')
    ordering = ('-date','-created_at')

@admin.register(NoticeClassroom)
class NoticeClassroomAdmin(admin.ModelAdmin):
    list_display = ('id', 'notice', 'classroom','created_at')
    list_filter = ('classroom', 'created_at')
    search_fields = ('notice__title', 'classroom__name')
    ordering = ('-created_at',)


