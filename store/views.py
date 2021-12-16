from django.shortcuts import render, get_object_or_404, redirect
from orders.models import OrderProduct
from store.forms import ReviewForm
from store.models import Product, Review, ProductGallery
from category.models import Category
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.contrib import messages


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
    is_purchased = False
    if request.user.is_authenticated:
        try:
            is_purchased = OrderProduct.objects.filter(user=request.user, product_id=product.id).exists()
        except OrderProduct.DoesNotExist:
            pass
    reviews = Review.objects.filter(product_id=product.id)
    product_gallery = ProductGallery.objects.filter(product=product)
    context = {
        'product': product,
        'is_purchased': is_purchased,
        'reviews': reviews,
        'product_gallery': product_gallery
    }
    return render(request, 'store/product_details.html', context)


def submit_review(request, product_id):
    redirect_path = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            review = Review.objects.get(user=request.user, product_id=product_id)
            review_form = ReviewForm(request.POST, instance=review)
            review_form.save()
            messages.success(request, 'Your review is updated.')
            return redirect(redirect_path)
        except Review.DoesNotExist:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = Review()
                review.product_id = product_id
                review.user = request.user
                review.subject = review_form.cleaned_data['subject']
                review.rating = review_form.cleaned_data['rating']
                review.review = review_form.cleaned_data['review']
                review.ip = request.META.get('REMOTE_ADDR')
                review.save()
                messages.success(request, 'Your review is added.')
                return redirect(redirect_path)