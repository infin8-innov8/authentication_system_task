from django.shortcuts import render, redirect 
# from django.http import HttpResponse
from django.contrib import messages 
from django.utils import timezone
from .models import UserAccount
from django.contrib.auth.hashers import make_password

def registration_page(request) : 
    context = { 
        'username' : '', 
        'first_name' : '', 
        'last_name' : '', 
        'email' : '', 
        'phone_number' : '',
    }

    if request.method == 'POST' : 
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")

        context.update({
            'username'      : username, 
            'first_name'    : first_name, 
            'last_name'     : last_name, 
            'email'         : email, 
            'phone_number'  : phone_number,
            })
   
        if UserAccount.objects.filter(email=email).exists() : 
            messages.error(request, "Email address already exists, kindly login or try via another email.", extra_tags="emailexist")
            return render(request=request, template_name = 'accounts/registrationtemp.html', context=context)
        
        if UserAccount.objects.filter(username=username).exists(): 
            messages.error(request, "Username is already tacken, try another", extra_tags="usernameexist")
            return render(request=request, template_name='accounts/registrationtemp.html', context=context)
        
        request.session['registrationdata'] = {
            'username'      : username, 
            'first_name'    : first_name, 
            'last_name'     : last_name, 
            'email'         : email, 
            'phone_number'  : phone_number,
        }
        return redirect('/verification')
    return render(request=request, template_name='accounts/registrationtemp.html', context=context)

def verification_page(request) : 
    registration_data = request.session.get('registrationdata')

    if request.method == 'POST':
        phone_otp = request.POST.get("phone_otp")
        email_otp = request.POST.get("email_otp")
        password = request.POST.get("password")
        
        if phone_otp != "111111" or email_otp != "222222":
            messages.error(request, "Invalid OTP entered.")
            return render(request, 'accounts/verificationtemp.html', {
                'email' : registration_data['email'],
                'phone_number' : registration_data['phone_number'],
                'has_phone' : bool(registration_data['phone_number']),
            })

        # Save the user securely
        user = UserAccount(
            username = registration_data['username'],
            first_name = registration_data['first_name'],
            last_name = registration_data['last_name'],
            email = registration_data['email'],
            phone_number = registration_data['phone_number'],
            password = make_password(password),  
            date_joined = timezone.now(),
        )

        user.save()
        messages.success(request, "Registration successful, kindly singin.", extra_tags="registrationsuccessful")
        request.session.pop('registrationdata', None)
        return redirect('/register')

    return render(request, 'accounts/verificationtemp.html', {
        'email': registration_data['email'],
        'phone_number': registration_data['phone_number'],
        'has_phone': bool(registration_data['phone_number']),
    })
     
def login_page(request) : 
    return render(request, 'accounts/logintemp.html')

def reset_password_page(request) : 
    return render(request, 'accounts/reset_passwordtemp.html')

def forgot_password_page(request) : 
    return render(request, 'accounts/forgot_passwordtemp.html')

def home_page(request) : 
    return render(request, 'accounts/hometemp.html')

