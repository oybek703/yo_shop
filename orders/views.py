import datetime

from django.http import JsonResponse
from django.shortcuts import render, redirect
from carts.models import CartItem
from orders.forms import OrderForm
from orders.models import Order
import json


def place_order(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)
    count_items = cart_items.count()
    if count_items == 0:
        return redirect('store')
    total = 0
    tax = 2
    for cart_item in cart_items:
        total += cart_item.product.price*cart_item.quantity
    total_with_tax = total + (2*total/100)
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            # Store all billing information in Order table
            cleaned_data = order_form.cleaned_data
            data = Order()
            data.user = user
            data.first_name = cleaned_data['first_name']
            data.last_name = cleaned_data['last_name']
            data.email = cleaned_data['email']
            data.phone_number = cleaned_data['phone_number']
            data.address_line_1 = cleaned_data['address_line_1']
            data.address_line_2 = cleaned_data['address_line_2']
            data.country = cleaned_data['country']
            data.city = cleaned_data['city']
            data.state = cleaned_data['state']
            data.order_note = cleaned_data['order_note']
            data.total = total_with_tax
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")  # 20210305
            order_number = f'{current_date}{data.id}'
            data.order_number = order_number
            data.save()
            order = Order.objects.get(user=user, is_ordered=False, order_number=order_number)
            order.save()
            context = {
                'cart_items': cart_items,
                'order': order,
                'total': total,
                'tax': tax,
                'total_with_tax': total_with_tax
            }
            return render(request, 'orders/place_order.html', context)
        else:
            return render(request, 'store/checkout.html', {'form': order_form})
    else:
        return redirect('checkout')


def payments(request):
    body = json.loads(request.body)
    print(body)
    res = {
        'data2': 'ok too.'
    }
    return JsonResponse(res)
