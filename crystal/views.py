from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product, ProductReview, ProductQA
from .forms import ProductReviewForm, ProductQAForm
import random

def home_view(request):
    categories = Category.objects.filter(show_in_homepage=True)
    context = {'categories': categories}
    return render(request, 'home.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_active=True)

    # Sorting
    sort = request.GET.get('sort')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')

    # Sidebar categories
    all_categories = Category.objects.all()

    context = {
        'category': category,
        'products': products,
        'all_categories': all_categories,
    }
    return render(request, 'crystal/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    gallery = product.images.all()
    watching_count = random.randint(5, 30)

    review_form = ProductReviewForm()
    qa_form = ProductQAForm()

    if request.method == 'POST' and request.user.is_authenticated:
        # REVIEW SUBMIT
        if 'rating' in request.POST:
            review_form = ProductReviewForm(request.POST)
            if review_form.is_valid():
                ProductReview.objects.update_or_create(
                    product=product,
                    user=request.user,
                    defaults=review_form.cleaned_data
                )
                return redirect(product.get_absolute_url())

        # QUESTION SUBMIT
        if 'question' in request.POST:
            qa_form = ProductQAForm(request.POST)
            if qa_form.is_valid():
                qa = qa_form.save(commit=False)
                qa.product = product
                qa.user = request.user
                qa.save()
                return redirect(product.get_absolute_url())

    context = {
        'product': product,
        'gallery': gallery,
        'watching_count': watching_count,
        'review_form': review_form,
        'qa_form': qa_form,
    }
    return render(request, 'crystal/product_detail.html', context)
