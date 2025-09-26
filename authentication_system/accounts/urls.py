from . import views 
from django.urls import path

urlpatterns = [
    path('login/', view=views.login_page, name='login'),
    path('register/', view=views.registration_page, name='register'),
    path('verification/', view=views.verification_page, name='verification'),
    path('reset_password/', view=views.reset_password_page, name='password reset'),
    path('forgot_password/', view=views.forgot_password_page, name='forgot password'),
    path('home/', view=views.home_page, name='home'),
    path('profile/', view = views.user_profile_page, name='User Profile'),
]
