from django.contrib import admin
from .models import Post

admin.site.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'caption', 'location', 'filter', 'created_at')