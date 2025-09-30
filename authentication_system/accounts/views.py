from django.shortcuts import render, redirect 
from django.contrib import messages 
from django.utils import timezone
from .models import UserAccount
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login
from django.conf import settings
import ldap 
from django.contrib.auth.decorators import login_required

def registration_page(request): 
    context = { 
        'username': '', 
        'first_name': '', 
        'last_name': '', 
        'email': '', 
        'phone_number': '',
    }

    if request.method == 'POST': 
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")

        # Validate required fields
        if not all([username, first_name, last_name, email]):
            messages.error(request, "Please fill in all required fields.", extra_tags="missing_fields")
            context.update({
                'username': username or '', 
                'first_name': first_name or '', 
                'last_name': last_name or '', 
                'email': email or '', 
                'phone_number': phone_number or '',
            })
            return render(request=request, template_name='accounts/registrationtemp.html', context=context)
   
        if UserAccount.objects.filter(email=email).exists(): 
            messages.error(request, "Email address already exists, kindly login or try via another email address.", extra_tags="emailexist")
            context.update({
                'username': username, 
                'first_name': first_name, 
                'last_name': last_name, 
                'email': email, 
                'phone_number': phone_number,
            })
            return render(request=request, template_name='accounts/registrationtemp.html', context=context)
        
        if UserAccount.objects.filter(username=username).exists(): 
            messages.error(request, "Username is already taken, try another", extra_tags="usernameexist")
            context.update({
                'username': username, 
                'first_name': first_name, 
                'last_name': last_name, 
                'email': email, 
                'phone_number': phone_number,
            })
            return render(request=request, template_name='accounts/registrationtemp.html', context=context)
        
        request.session['registrationdata'] = {
            'username': username, 
            'first_name': first_name, 
            'last_name': last_name, 
            'email': email, 
            'phone_number': phone_number or '',
        }
        return redirect('/verification')
    
    return render(request=request, template_name='accounts/registrationtemp.html', context=context)

def verification_page(request): 
    registration_data = request.session.get('registrationdata')
    
    # Check if registration data exists
    if not registration_data:
        messages.error(request, "Registration session expired or invalid. Please start registration again.")
        return redirect('/register')
    
    # Check if required fields are present
    required_fields = ['username', 'first_name', 'last_name', 'email']
    for field in required_fields:
        if field not in registration_data or not registration_data[field]:
            messages.error(request, f"Missing required field: {field}. Please start registration again.")
            return redirect('/register')

    if request.method == 'POST':
        phone_otp = request.POST.get("phone_otp")
        email_otp = request.POST.get("email_otp")
        password = request.POST.get("password")
        
        # Validate OTP and password
        if not all([phone_otp, email_otp, password]):
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'accounts/verificationtemp.html', {
                'email': registration_data['email'],
                'phone_number': registration_data.get('phone_number', ''),
                'has_phone': bool(registration_data.get('phone_number')),
            })
        
        if phone_otp != "111111" or email_otp != "222222":
            messages.error(request, "Invalid OTP entered.")
            return render(request, 'accounts/verificationtemp.html', {
                'email': registration_data['email'],
                'phone_number': registration_data.get('phone_number', ''),
                'has_phone': bool(registration_data.get('phone_number')),
            })

        # LDAP User creation
        try: 
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
            attrs['mail'] = registration_data['email'].encode('utf-8')

            if registration_data.get('phone_number'):
                attrs['telephoneNumber'] = registration_data['phone_number'].encode('utf-8')

            # Add the user to the LDAP directory
            con.add_s(dn, list(attrs.items()))
            con.unbind_s()

        except ldap.ALREADY_EXISTS:
            messages.error(request, "This user already exists in the LDAP directory.", extra_tags="userexist")
            return redirect('/register/')
        
        except Exception as e:
            messages.error(request, f"An error occurred with the LDAP server: {str(e)}")
            return redirect('/register/')

        # Create local database user
        user = UserAccount(
            username=registration_data['username'],
            first_name=registration_data['first_name'],
            last_name=registration_data['last_name'],
            email=registration_data['email'],
            phone_number=registration_data.get('phone_number', ''),
            password=make_password(password),  
            date_joined=timezone.now(),
        ) 
        user.save()

        messages.success(request, "Registration successful, kindly sign in.", extra_tags="registrationsuccessful")
        request.session.pop('registrationdata', None)
        return redirect('/register')

    return render(request, 'accounts/verificationtemp.html', {
        'email': registration_data['email'],
        'phone_number': registration_data.get('phone_number', ''),
        'has_phone': bool(registration_data.get('phone_number')),
    })
     
def login_page(request):
    context = {
        "credential": '',
    }
    if request.method == "POST":
        credential = request.POST.get("credential")
        password = request.POST.get("password")

        if not credential or not password:
            messages.error(request, "Please enter both credential and password.", extra_tags="missing_fields")
            return render(request, 'accounts/logintemp.html', context=context)

        # if credential is an email
        if "@" in credential:
            try:
                user_account = UserAccount.objects.get(email=credential)
                username = user_account.username
            except UserAccount.DoesNotExist:
                messages.error(request, "No account found with this email address", extra_tags="usernotexist")
                context['credential'] = credential
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
            else:
                messages.error(request, "No account found with this username", extra_tags="usernotexist")

            context['credential'] = credential
            return render(request, 'accounts/logintemp.html', context=context)
    
    return render(request, 'accounts/logintemp.html', context=context)

def reset_password_page(request): 
    return render(request, 'accounts/reset_passwordtemp.html')

def forgot_password_page(request): 
    return render(request, 'accounts/forgot_passwordtemp.html')

@login_required
def home_page(request): 
    user = request.user
    return render(request, 'accounts/hometemp.html', context={'name': user.first_name.upper()})

@login_required
def user_profile_page(request): 
    user = request.user

    if request.method == 'POST': 
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        
        # Validate required fields
        if not all([first_name, last_name, username, email]):
            messages.error(request, "Please fill in all required fields.", extra_tags="missing_fields")
            return render(request, 'accounts/user_informationtemp.html', context={'user': user})
        
        try: 
            # Check if username is being changed and if new username already exists
            if username != user.username and UserAccount.objects.filter(username=username).exists():
                messages.error(request, "Username is already taken. Please choose a different username.", extra_tags="usernameexist")
                return render(request, 'accounts/user_informationtemp.html', context={'user': user})
            
            # Check if email is being changed and if new email already exists
            if email != user.email and UserAccount.objects.filter(email=email).exists():
                messages.error(request, "Email address is already registered. Please use a different email.", extra_tags="emailexist")
                return render(request, 'accounts/user_informationtemp.html', context={'user': user})

            # Connection and updating values in LDAP
            con = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
            con.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
            base_dn = settings.AUTH_LDAP_USER_SEARCH.base_dn
            
            # Use the original username to find the DN (in case username is being changed)
            old_dn = f"uid={user.username},{base_dn}"
            
            # Prepare modification attributes
            mod_attrs = [
                (ldap.MOD_REPLACE, 'givenName', [first_name.encode('utf-8')]),
                (ldap.MOD_REPLACE, 'sn', [last_name.encode('utf-8')]),
                (ldap.MOD_REPLACE, 'mail', [email.encode('utf-8')]),
                (ldap.MOD_REPLACE, 'telephoneNumber', [phone_number.encode('utf-8')] if phone_number else []),
                (ldap.MOD_REPLACE, 'cn', [f"{first_name} {last_name}".encode('utf-8')]),
            ]
            
            # If username is being changed, we need to handle it specially
            if username != user.username:
                mod_attrs.append((ldap.MOD_REPLACE, 'uid', [username.encode('utf-8')]))
                # Create new DN with new username
                new_rdn = f"uid={username}"
                # Modify the DN (rename the entry)
                con.modrdn_s(old_dn, new_rdn, True)
                # Now update other attributes using the new DN
                new_dn = f"{new_rdn},{base_dn}"
                con.modify_s(new_dn, mod_attrs)
            else:
                # If username is not changing, just modify the attributes
                con.modify_s(old_dn, mod_attrs)
            
            con.unbind_s()

            # Update database values
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.email = email 
            user.phone_number = phone_number or ''
            user.save()

            messages.success(request, 'Your profile has been updated successfully!', extra_tags='user-update-success')
            return redirect('/profile')

        except ldap.NO_SUCH_OBJECT:
            messages.error(request, f"User '{user.username}' not found in LDAP. Local profile was updated, but LDAP was not.")
            # Still update the local database
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.email = email 
            user.phone_number = phone_number or ''
            user.save()
            messages.success(request, 'Your local profile has been updated successfully!', extra_tags='user-update-success')
            return redirect('/profile')

        except Exception as e: 
            messages.error(request, f'Error updating profile: {str(e)}', extra_tags='error')
    
    return render(request, 'accounts/user_informationtemp.html', context={'user': user})