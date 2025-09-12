from django.shortcuts import render

def registration_page(request) : 
    return render(request, 'registrationtemp.html')
    
    
def verification_page(request) : 
    return render(request, 'verificationtemp.html')