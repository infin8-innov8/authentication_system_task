from . import views 
from django.urls import path

urlpatterns = [
    path('register/', views.registration_page),
    path('verification/', views.verification_page)
]
