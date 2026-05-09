from .models import Category

def crystal_categories(request):
    return {
        'crystal_categories': Category.objects.filter(show_in_homepage=True)
    }
