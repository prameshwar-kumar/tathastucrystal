# tathastucrystal/views.py

from django.shortcuts import render
from blog.models import BlogPost, BlogCategory
from crystal.models import Category as CrystalCategory
from worship.models import Category as WorshipCategory



def home(request):
    crystal_categories = CrystalCategory.objects.filter(show_in_homepage=True)
    worship_categories = WorshipCategory.objects.filter(show_in_homepage=True)
    blogs = BlogPost.objects.all().prefetch_related('related_crystals', 'related_worship')[:5]  # latest 5

    context = {
        'crystal_categories': crystal_categories,
        'worship_categories': worship_categories,
        'blogs': blogs,
    }
    return render(request, 'home.html', context)

