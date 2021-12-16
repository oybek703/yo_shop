import datetime
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from carts.models import CartItem
from orders.forms import OrderForm
from orders.models import Order, Payment, OrderProduct
import json
from store.models import Product


def place_order(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)
    count_items = cart_items.count()
    if count_items == 0:
        return redirect('store')
    total = 0
    for cart_item in cart_items:
        total += cart_item.product.price*cart_item.quantity
    tax = round(0.02 * total, 2)
    total_with_tax = total + tax
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
            data.tax = tax
            data.total = total_with_tax
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
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['order_number'])
    payment = Payment(
        payment_id=body['transaction_id'],
        user=request.user,
        payment_method=body['payment_method'],
        paid_amount=order.total,
        status=body['status']
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move cart items to OrderProduct table
    cart_items = CartItem.objects.filter(user=request.user)
    for cart_item in cart_items:
        order_product = OrderProduct()
        order_product.order = order
        order_product.payment = payment
        order_product.user = request.user
        order_product.product = cart_item.product
        order_product.product_quantity = cart_item.quantity
        order_product.product_price = cart_item.product.price
        order_product.ordered = True
        order_product.save()
        cart_item_updated = CartItem.objects.get(pk=cart_item.id)
        product_variations = cart_item_updated.variations.all()
        order_product_updated = OrderProduct.objects.get(pk=order_product.id)
        order_product_updated.variations.set(product_variations)
        order_product_updated.save()

    # Reduce the quantity of sold products
        product = Product.objects.get(pk=cart_item.product.id)
        product.stock -= cart_item.quantity
        product.save()
    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send mail to user that payment accepted
    mail_subject = 'Payment success.'
    message = render_to_string('orders/payment_success.html', {
        'user': order.user,
        'order': order
    })
    to_email = order.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # Send order number and transaction id back to frontend
    res = {
        'orderNumber': order.order_number,
        'transId': payment.payment_id
    }
    return JsonResponse(res)


def order_complete(request):
    order_number = request.GET.get('order-number')
    transaction_id = request.GET.get('transaction-id')
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order)
        payment = Payment.objects.get(payment_id=transaction_id)
        total = 0
        for order_item in ordered_products:
            total += order_item.product_price * order_item.product_quantity
        tax = total * 2/100
        context = {
            'order': order,
            'ordered_products': ordered_products,
            'transaction_id': transaction_id,
            'total': total,
            'tax': tax,
            'payment': payment
        }
        return render(request, 'orders/order_complete.html', context)
    except OrderProduct.DoesNotExist or Order.DoesNotExist or Payment.DoesNotExist:
        return redirect('home')
