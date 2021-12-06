from django.shortcuts import render, get_object_or_404
from store.models import Product
from category.models import Category


def store(request, slug=None):
    category = None
    products = Product.objects.all().filter(is_available=True)
    if slug:
        category = get_object_or_404(Category, slug=slug)
        products = Product.objects.all().filter(is_available=True, category__slug=slug)
    categories = Category.objects.all()
    products_count = products.count()
    context = {
        'products': products,
        'count': products_count,
        'selected_category': category
    }
    return render(request, 'store/store.html', context)
