from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index, name='index'),

    path('register/', views.register, name='register'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('login_view/', views.login_view, name='login_view'),
    # path('customer_profile/', views.customer_profile, name='customer_profile'),
    path('admin_profile/', views.admin_profile, name='admin_profile'),
    path('change_password/', views.change_password, name='change_password'),

    # Add other URL patterns as needed   
]
