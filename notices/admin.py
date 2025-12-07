from django.contrib import admin
from .models import Notice,NoticeClassroom

class NoticeClassroomInline(admin.TabularInline):
    model = NoticeClassroom
    extra = 1 # 空行を1行表示

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'nursery', 'date', 'category', 'created_at')
    list_filter = ('nursery','date','category')
    search_fields =('title','body')
    inlines = [NoticeClassroomInline]

@admin.register(NoticeClassroom)
class NoticeClassroomAdmin(admin.ModelAdmin):
    list_display = ('notice', 'classroom','created_at','updated_at')
    list_filter = ('classroom',)


