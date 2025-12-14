from django.contrib import admin
from .models import Board, BoardPost

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'date', 'nursery', 'user', 'created_at')
    list_filter = ('category', 'date', 'nursery')
    search_fields = ('title',)

@admin.register(BoardPost)
class BoardPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'board', 'user', 'comment', 'created_at')
    search_fields = ('board' ,'user')