from django.contrib import admin
from .models import DetectionLog, FindLog


@admin.register(DetectionLog)
class DetectionLogAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username', 'detected', 'input_text', 'created_at')
    list_filter = ('detected',)
    search_fields = ('user_id', 'username', 'input_text', 'detected')
    readonly_fields = ('created_at',)


@admin.register(FindLog)
class FindLogAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username', 'query', 'found', 'created_at')
    list_filter = ('found',)
    search_fields = ('user_id', 'username', 'query')
    readonly_fields = ('created_at',)