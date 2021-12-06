from django.shortcuts import render
from store.models import Product


def index(request, slug=None):
    products = Product.objects.all().filter(is_available=True)
    if slug:
        print(slug)
    context = {
        'products': products
    }
    return render(request, 'home.html', context)
