from django.contrib import admin
from .models import Board, BoardPost

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'date', 'nursery', 'user', 'created_at')
    list_filter = ('category', 'date', 'nursery')
    search_fields = ('title', 'user__username')
    ordering = ('-date', '-created_at')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(nursery=request.user.nursery)

@admin.register(BoardPost)
class BoardPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'board', 'user', 'comment', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('board__title' ,'user__username', 'comment')
    ordering = ('-created_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(nursery=request.user.nursery)
