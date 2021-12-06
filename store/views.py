from django.shortcuts import render, get_object_or_404
from store.models import Product
from category.models import Category


def store(request, category_slug=None):
    category = None
    products = Product.objects.all().filter(is_available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.all().filter(is_available=True, category__slug=category_slug)
    products_count = products.count()
    context = {
        'products': products,
        'count': products_count,
        'selected_category': category
    }
    return render(request, 'store/store.html', context)


def product_details(request, category_slug, product_slug):
    category = get_object_or_404(Category, slug=category_slug)
    product = get_object_or_404(Product, slug=product_slug)
    context = {
        'product': product
    }
    return render(request, 'store/product-details.html', context)
