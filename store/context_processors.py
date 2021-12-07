from carts.models import Cart, CartItem
from carts.views import get_cart_id


def count_cart_items(request):
    cart_items_count = 0
    if 'admin' in request:
        return {}
    else:
        try:
            try:
                cart = Cart.objects.get(cart_id=get_cart_id(request))  # get cart
            except Cart.DoesNotExist:
                cart = Cart.objects.create(cart_id=get_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart)
            for cart_item in cart_items:
                cart_items_count += cart_item.quantity
        except CartItem.DoesNotExist:
            pass
        return dict(cart_items_count=cart_items_count)
