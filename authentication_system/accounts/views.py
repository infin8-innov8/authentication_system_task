from django.shortcuts import render, redirect 
from django.contrib import messages 
from django.utils import timezone
from .models import UserAccount
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login
from django.conf import settings
import ldap 

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
   
        # if UserAccount.objects.filter(email=email).exists() : 
        #     messages.error(request, "Email address already exists, kindly login or try via another email.", extra_tags="emailexist")
        #     return render(request=request, template_name = 'accounts/registrationtemp.html', context=context)
        
        # if UserAccount.objects.filter(username=username).exists(): 
        #     messages.error(request, "Username is already tacken, try another", extra_tags="usernameexist")
        #     return render(request=request, template_name='accounts/registrationtemp.html', context=context)
        
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

        # LDAP User creation
        try : 
            con = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
            con.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)

            base_dn = settings.AUTH_LDAP_USER_SEARCH.base_dn
            dn = f"uid={registration_data['username']},{base_dn}"
            
            attrs = {}
            attrs['objectClass'] = [b'top', b'person', b'organizationalPerson', b'inetOrgPerson']
            attrs['cn'] = registration_data['first_name'].encode('utf-8')
            attrs['sn'] = registration_data['last_name'].encode('utf-8')
            attrs['uid'] = registration_data['username'].encode('utf-8')
            attrs['userPassword'] = password.encode('utf-8')

            if registration_data.get('email'):
                attrs['mail'] = registration_data['email'].encode('utf-8')

            if registration_data.get('phone_number'):
                attrs['telephoneNumber'] = registration_data['phone_number'].encode('utf-8')

        # 4. Add the user to the LDAP directory
            con.add_s(dn, list(attrs.items()))
            con.unbind_s()

        except ldap.ALREADY_EXISTS:
            messages.error(request, "This user already exists in the LDAP directory.", extra_tags= "userexist")
            return redirect('/register/')
        
        except Exception as e:
            messages.error(request, f"An error occurred with the LDAP server: {e}")
            return redirect('/register/')

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

        messages.success(request, "Registration successful, kindly sing in.", extra_tags="registrationsuccessful")
        request.session.pop('registrationdata', None)
        return redirect('/register')

    return render(request, 'accounts/verificationtemp.html', {
        'email': registration_data['email'],
        'phone_number': registration_data['phone_number'],
        'has_phone': bool(registration_data['phone_number']),
    })
     
def login_page(request):
    context = {
        "credential": '',
    }
    if request.method == "POST":
        credential = request.POST.get("credential")
        password = request.POST.get("password")

        # if credential is a email
        if "@" in credential:
            try:
                user_account = UserAccount.objects.get(email=credential)
                username = user_account.username
            except UserAccount.DoesNotExist:
                messages.error(request, "No account found with this email address", extra_tags="usernotexist")
                return render(request, 'accounts/logintemp.html', context=context)
        else:
            username = credential

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            if UserAccount.objects.filter(username=username).exists():
                messages.error(request, "Incorrect password, Please try again.", extra_tags="wrongpassword")
            
            return render(request, 'accounts/logintemp.html', context=context)
    
    return render(request, 'accounts/logintemp.html', context=context)

def reset_password_page(request) : 
    return render(request, 'accounts/reset_passwordtemp.html')

def forgot_password_page(request) : 
    return render(request, 'accounts/forgot_passwordtemp.html')

def home_page(request) : 
    return render(request, 'accounts/hometemp.html')


