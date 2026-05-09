# worship/admin.py
from django.contrib import admin
from django.utils.html import format_html, mark_safe
from .models import Brand, Category, Product, ProductImage, ProductReview, ProductQA

# -------------------- Brand Admin --------------------
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# -------------------- Category Admin --------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'show_in_homepage', 'image_thumb', 'slug')
    list_filter = ('show_in_homepage',)
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ('image_preview',)

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'image', 'image_preview', 'show_in_homepage')
        }),
    )

    def image_thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px; object-fit:contain;" />', obj.image.url)
        return "-"
    image_thumb.short_description = "Thumb"

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:200px; object-fit:contain;" />', obj.image.url)
        return "No image"
    image_preview.short_description = "Image Preview"


# -------------------- Product Image Inline --------------------
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'order', 'thumbnail')
    readonly_fields = ('thumbnail',)

    def thumbnail(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" style="height:60px; object-fit:contain;" />', obj.image.url)
        return "-"
    thumbnail.short_description = "Thumb"


# -------------------- Product Admin --------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'brand', 'category', 'price', 'discount_price', 'stock',
        'weight', 'length', 'width', 'height', 'is_active', 'created_at'
    )
    list_filter = ('is_active', 'brand', 'category')
    search_fields = ('name', 'brand__name', 'category__name')
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]
    readonly_fields = ('gallery_preview',)

    fieldsets = (
        (None, {
            'fields': (
                'name', 'slug', 'brand', 'category',
                'short_description', 'description',
                'price', 'discount_price', 'stock',
                'weight', 'length', 'width', 'height',
                'is_active'
            )
        }),
        ('Gallery', {
            'fields': ('gallery_preview',),
        }),
    )

    def gallery_preview(self, obj):
        imgs = obj.images.all()[:6]
        if imgs:
            html = ''
            for i in imgs:
                html += f'<img src="{i.image.url}" style="height:80px; object-fit:contain; margin-right:6px;" />'
            return mark_safe(html)
        return "No images"
    gallery_preview.short_description = "Gallery preview"


# -------------------- Product Review Admin --------------------
@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'comment')


# -------------------- Product QA Admin --------------------
@admin.register(ProductQA)
class ProductQAAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'question', 'answer', 'created_at')
    search_fields = ('product__name', 'user__username', 'question', 'answer')
