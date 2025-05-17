from django.contrib import admin
from .models import Post
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'reel', 'reason', 'created_at')
    search_fields = ('user__username', 'reel__id', 'reason')
    list_filter = ('created_at',)
admin.site.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'caption', 'location', 'filter', 'created_at')
    