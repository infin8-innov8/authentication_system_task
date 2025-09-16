from django.shortcuts import render, redirect 
from django.http import HttpResponse
from django.utils import timezone
from .models import UserAccount
from django.contrib.auth.hashers import make_password

def registration_page(request) : 
    if request.method == 'POST' : 
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        print(first_name, last_name, username, email, phone_number, sep="\n")
        
        user = UserAccount(
            username = username,
            first_name = first_name,
            last_name = last_name,
            email = email,
            phone_number = phone_number, 
            date_joined = timezone.now()
        )

        user.save()
        return redirect('/register/')
    return render(request, 'accounts/registrationtemp.html')

def verification_page(request) : 
    return render(request, 'accounts/verificationtemp.html')

def login_page(request) : 
    return render(request, 'accounts/logintemp.html')

def reset_password_page(request) : 
    return render(request, 'accounts/reset_passwordtemp.html')

def forgot_password_page(request) : 
    return render(request, 'accounts/forgot_passwordtemp.html')

def home_page(request) : 
    return render(request, 'accounts/hometemp.html')