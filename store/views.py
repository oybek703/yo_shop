from django.shortcuts import render, get_object_or_404
from carts.views import get_cart_id
from store.models import Product
from category.models import Category
from carts.models import CartItem, Cart
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q


def get_with_pagination(request, products, num_pages=3):
    page = request.GET.get('page', 1)
    paginator = Paginator(products, num_pages)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    return products


def store(request, category_slug=None):
    category = None
    products = Product.objects.all().filter(is_available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.all().filter(is_available=True, category__slug=category_slug)
    products_count = products.count()
    products = get_with_pagination(request, products)
    context = {
        'products': products,
        'count': products_count,
        'selected_category': category
    }
    return render(request, 'store/store.html', context)


def search(request):
    count = 0
    products = Product.objects.filter(is_available=True).order_by('-created_date')
    keyword = request.GET.get('keyword')
    if keyword:
        products = products.filter(Q(description__icontains=keyword) | Q(name__icontains=keyword))
        count = products.count()
        products = get_with_pagination(request, products)
    context = {
        'products': products,
        'count': count
    }
    return render(request, 'store/store.html', context)


def product_details(request, category_slug, product_slug):
    category = get_object_or_404(Category, slug=category_slug)
    product = get_object_or_404(Product, slug=product_slug, category=category)
    cart = Cart.objects.get(cart_id=get_cart_id(request))
    in_cart = CartItem.objects.filter(product=product, cart=cart).exists()
    context = {
        'product': product,
        'in_cart': in_cart
    }
    return render(request, 'store/product_details.html', context)