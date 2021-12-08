from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from store.models import Product, Variation
from .models import Cart, CartItem


def get_cart_id(request):
    cart_id = request.session.session_key
    if not cart_id:
        cart_id = request.session.create()
    return cart_id


def add_to_cart(request, product_id):
    product = Product.objects.get(pk=product_id)  # get product
    product_variations = []
    if request.method == 'POST':
        for key in request.POST:
            value = request.POST[key]
            try:
                variation = Variation.objects.get(
                    product=product,
                    category__iexact=key,
                    value__iexact=value
                )
                product_variations.append(variation)
            except Variation.DoesNotExist:
                pass
    try:
        cart = Cart.objects.get(cart_id=get_cart_id(request))  # get cart
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=get_cart_id(request))
    cart.save()
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1  # increment quantity
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
    if len(product_variations) > 0:
        cart_item.variations.clear()
        for variation in product_variations:
            cart_item.variations.add(variation)
    cart_item.save()
    redirect_path = reverse('cart')
    return HttpResponseRedirect(redirect_path)


def remove_from_cart(request, product_id):
    if request.method == 'GET':
        cart_item = CartItem.objects.get(product=product_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    else:
        product_id = request.POST['product_id']
        cart_item = CartItem.objects.get(product=product_id)
        cart_item.delete()
    redirect_path = reverse('cart')
    return HttpResponseRedirect(redirect_path)


def cart_page(request, total=0, quantity=0, cart_items=None):
    tax = 0
    total_with_tax = 0
    try:
        cart = Cart.objects.get(cart_id=get_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = 0.02 * total
        total_with_tax = total + tax
    except Cart.DoesNotExist or CartItem.DoesNotExist:
        pass
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'total_with_tax': total_with_tax
    }
    return render(request, 'store/cart.html', context)
