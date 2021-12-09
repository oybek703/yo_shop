from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail, EmailMessage
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from .forms import RegistrationForm
from django.contrib import messages, auth
from .models import Account
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


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
            username = f'{first_name.lower()}__{last_name.lower()}'
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
            auth.login(request, user)
            messages.success(request, 'You are logged in successfully.')
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
    return render(request, 'accounts/dashboard.html')
