from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from carts.models import Cart, CartItem
from carts.views import get_cart_id
from orders.models import Order
from .forms import RegistrationForm
from django.contrib import messages, auth
from .models import Account
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
import uuid


def register(request):
    registration_from = RegistrationForm()
    if request.method == 'POST':
        registration_from = RegistrationForm(request.POST)
        if registration_from.is_valid():
            first_name = registration_from.cleaned_data['first_name']
            last_name = registration_from.cleaned_data['last_name']
            email = registration_from.cleaned_data['email']
            phone_number = registration_from.cleaned_data['phone_number']
            password = registration_from.cleaned_data['password']
            username = f'{uuid.uuid4()}'
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password
            )
            user.phone_number = phone_number
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Verify email address.'
            message = render_to_string('accounts/email_verification.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            return redirect(f'/accounts/login/?command=verification&email={email}')
    context = {
        'form': registration_from
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        if user is None:
            messages.error(request, 'Invalid user credentials.')
            return redirect('login')
        else:
            try:
                cart = Cart.objects.get(cart_id=get_cart_id(request))
                cart_items = CartItem.objects.filter(cart=cart)
                product_variations = []
                for cart_item in cart_items:
                    cart_item_variations = cart_item.variations.all()
                    product_variations.append(list(cart_item_variations))
                existing_variations = []
                ids = []
                user_cart_items = CartItem.objects.filter(user=user)
                for user_cart_item in user_cart_items:
                    user_cart_item_variations = user_cart_item.variations.all()
                    existing_variations.append(list(user_cart_item_variations))
                    ids.append(user_cart_item.id)
                for product_variation in product_variations:
                    if product_variation in existing_variations:
                        cart_variation_index = existing_variations.index(product_variation)
                        cart_item_id = ids[cart_variation_index]
                        user_cart_item = CartItem.objects.get(id=cart_item_id)
                        user_cart_item.quantity += 1
                        user_cart_item.save()
                    else:
                        cart_items = CartItem.objects.filter(cart=cart)
                        for cart_item in cart_items:
                            cart_item.user = user
                            cart_item.save()
            except Cart.DoesNotExist or CartItem.DoesNotExist:
                pass
            auth.login(request, user)
            messages.success(request, 'You are logged in successfully.')
            try:
                redirect_path = request.META.get('HTTP_REFERER').split('next=')[1]
                return redirect(redirect_path)
            except IndexError:
                pass
            return redirect('dashboard')
    return render(request, 'accounts/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account activated successfully. You can login now.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link.')
        return redirect('register')


@login_required(login_url='login')
def dashboard(request):
    orders_count = Order.objects.filter(user=request.user, is_ordered=True).count()
    context = {
        'orders_count': orders_count
    }
    return render(request, 'accounts/dashboard.html', context)


def my_orders(request):
    user_orders = Order.objects.filter(user=request.user, is_ordered=True)
    context = {
        'orders': user_orders
    }
    return render(request, 'accounts/my_orders.html', context)


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        use_exists = Account.objects.filter(email=email).exists()
        if use_exists:
            user = Account.objects.get(email__exact=email)
            # Send reset password link to user email address
            current_site = get_current_site(request)
            mail_subject = 'Reset your password.'
            message = render_to_string('accounts/reset_password_validate.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'We have sent reset password link to your email. Please check your email.')
            return redirect('login')
        else:
            messages.error(request, 'User does not exist. Please enter your valid email address.')
            return redirect('forgot_password')
    return render(request, 'accounts/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        return redirect('reset_password')
    else:
        messages.error(request, 'Invalid activation link.')
        return redirect('login')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password != confirm_password:
            messages.error(request, 'Password confirmation should match.')
            return redirect('reset_password')
        else:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset success.')
            return redirect('login')
    else:
        return render(request, 'accounts/reset_password.html')
