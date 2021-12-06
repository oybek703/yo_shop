from django.shortcuts import render
from store.models import Product
from category.models import Category


def store(request, slug=None):
    products = Product.objects.all().filter(is_available=True)
    if slug:
        products = Product.objects.all().filter(is_available=True, category__slug=slug)
    categories = Category.objects.all()
    products_count = products.count()
    context = {
        'products': products,
        'count': products_count,
        'categories': categories
    }
    return render(request, 'store/store.html', context)
