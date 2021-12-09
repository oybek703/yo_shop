from django.shortcuts import render, redirect
from .forms import RegistrationForm
from django.contrib import messages, auth
from .models import Account


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
            messages.success(request, 'You registered successfully and can login now.')
            return redirect('login')
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
            # implement dashboard then
            # messages.success('You are logged in successfully.')
            return redirect('home')
    return render(request, 'accounts/login.html')


def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')
