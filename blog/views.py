from django.shortcuts import render, get_object_or_404
from .models import BlogPost, BlogCategory
from crystal.models import Category as CrystalCategory
from worship.models import Category as WorshipCategory

def blog_list(request):
    blogs = BlogPost.objects.all().prefetch_related('related_crystals', 'related_worship')
    categories = BlogCategory.objects.all()
    context = {
        'blogs': blogs,
        'blog_categories': categories,
    }
    return render(request, 'blog/blog_list.html', context)


def blog_detail(request, slug):
    blog = get_object_or_404(BlogPost.objects.prefetch_related('related_crystals', 'related_worship'), slug=slug)
    context = {
        'blog': blog
    }
    return render(request, 'blog/blog_detail.html', context)
