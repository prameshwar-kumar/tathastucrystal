# worship/context_processors.py
from .models import Category

def worship_categories(request):
    return {
        'worship_categories': Category.objects.filter(show_in_homepage=True)
    }
