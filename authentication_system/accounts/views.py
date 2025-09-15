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
        email_otp = request.POST.get("email_otp")
        phone_otp = request.POST.get("phone_otp")
        password = request.POST.get("password")
        conf_password = request.POST.get("confirm_password")
        # print(first_name, last_name, username, email, phone_number, email_otp, phone_otp, sep="\n")
        sent_email_otp = '111111'
        sent_phone_otp = '222222'

        if password != conf_password : 
            return render(request, 'accounts/registrationtemp.html', {'error' : 'Password do not match'})

        if email_otp != sent_email_otp or phone_otp != sent_phone_otp : 
            return render(request, 'accounts/registrationtemp.html', {'error' : 'invalid OTP varification'})
        
        user = UserAccount(
            username = username,
            first_name = first_name,
            last_name = last_name,
            email = email,
            password = make_password(password),
            phone_number = phone_number, 
            date_joined = timezone.now()
        )

        user.save()
        return redirect('/login/')
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