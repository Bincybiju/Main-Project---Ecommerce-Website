from django.shortcuts import render, redirect, HttpResponse
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from .forms import UserRegistrationForm, PasswordChangeForm
from .models import CustomUser
from django.contrib.auth import authenticate,login 
from django.contrib import messages
from django.db import IntegrityError
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash

User = get_user_model()

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to update the session with new password hash
            return HttpResponse('<script>alert("change password successfully."); window.location.href = "/customer_profile/";</script>')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})

def index(request):
    return render(request,'index.html')



def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.username = form.cleaned_data['username']  
                user.set_password(form.cleaned_data['password1'])  
                user.save()

                # Generate OTP and send email
                otp = get_random_string(length=6, allowed_chars='1234567890')
                subject = 'Email Verification OTP'
                message = f'Your OTP is: {otp}'
                send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
 
                # Store OTP and email in session for verification
                request.session['otp'] = otp
                request.session['email'] = user.email
 
                # Redirect to verify email page
                return redirect('verify_otp')
            except IntegrityError:
                form.add_error('email', 'Email address already in use. Please try another one.')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def verify_otp(request): 
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        expected_otp = request.session.get('otp')
 
        if entered_otp == expected_otp:
            user_email = request.session.get('email')
            user = User.objects.get(email=user_email)
            user.is_verified = True
            user.save()
            # OTP verification successful
            messages.success(request, 'Email verified successfully. You can now login.')
            del request.session['otp']
            return HttpResponse('<script>alert("Email verified successfully. You can now login."); window.location.href = "/login_view/";</script>')
        else:
            # OTP verification failed
            return HttpResponse('<script>alert("Invalid OTP. Please try again."); window.location.href = "/verify_otp/";</script>')

    return render(request, 'verify_otp.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Assuming you're using the default Django User model
        try:
            user = User.objects.get(email=email.lower())
        except User.DoesNotExist:
            user = None

        if user is not None:
            user = authenticate(username=user.username, password=password)
            print(user)
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    return redirect('admin_profile')
                else:
                    return redirect('customer_profile')
            else:
                return HttpResponse('<script>alert("Invalid email or password. Please try again."); window.location.href = "/login_view/";</script>')
        else:
            return HttpResponse('<script>alert("Invalid email or password. Please try again."); window.location.href = "/login_view/";</script>')

    return render(request, 'login.html')


@login_required
def admin_profile(request):
    # Check if the user is a superuser
    if not request.user.is_superuser:
        return HttpResponse("Unauthorized", status=401)  # Return unauthorized response

    # Render the admin profile page for superusers
    return render(request, 'admin_profile.html')

