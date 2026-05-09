from django.contrib import admin
from .models import BlogCategory, BlogPost

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name', 'show_in_homepage')


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at')
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ('related_crystals', 'related_worship')
