from django.contrib import admin
from .models import BlogPost

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_on')  # fixed field name
    search_fields = ('title', 'content')
    list_filter = ('created_on', 'author')
    ordering = ('-created_on',)
