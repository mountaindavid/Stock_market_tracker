from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from .forms import CustomUserCreationForm, CustomPasswordResetForm, CustomSetPasswordForm
from .models import User


def register(request):
    """Simple user registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('portfolios:portfolio_list')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    """Simple user login view"""
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('portfolios:portfolio_list')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'users/login.html')


@require_http_methods(["GET", "POST"])
def user_logout(request):
    """Logout with confirmation"""
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Logged out successfully!')
        return redirect('home')
    return render(request, 'users/logout_confirm.html')


@csrf_protect
def password_reset(request):
    """Password reset request view"""
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                # Generate password reset token
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Build reset URL
                current_site = get_current_site(request)
                reset_url = f"http://{current_site.domain}/users/reset/{uid}/{token}/"
                
                # Send email
                subject = "Password Reset Request - Stock Market Portfolio"
                message = render_to_string('users/password_reset_email.html', {
                    'user': user,
                    'reset_url': reset_url,
                    'site_name': current_site.name,
                })
                
                send_mail(
                    subject,
                    message,
                    None,  # Use DEFAULT_FROM_EMAIL
                    [email],
                    fail_silently=False,
                )
                
                messages.success(request, 
                    'Password reset email has been sent. Please check your email and follow the instructions.')
                return redirect('users:login')
                
            except User.DoesNotExist:
                # Don't reveal if user exists or not for security
                messages.success(request, 
                    'If an account with that email exists, a password reset email has been sent.')
                return redirect('users:login')
    else:
        form = CustomPasswordResetForm()
    
    return render(request, 'users/password_reset_form.html', {'form': form})


@csrf_protect
def password_reset_confirm(request, uidb64, token):
    """Password reset confirmation view"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = CustomSetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been successfully reset. You can now log in with your new password.')
                return redirect('users:login')
        else:
            form = CustomSetPasswordForm(user)
        
        return render(request, 'users/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'The password reset link is invalid or has expired. Please request a new one.')
        return redirect('users:password_reset')
