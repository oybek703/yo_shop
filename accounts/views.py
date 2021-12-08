from django.shortcuts import render
from .forms import RegistrationForm


def register(request):
    registration_from = RegistrationForm()
    context = {
        'form': registration_from
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    return render(request, 'accounts/login.html')


def logout(request):
    pass
