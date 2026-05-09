from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import LoginForm


@require_http_methods(['GET', 'POST'])
def login_view(request):
    """
    Handle user login.
    GET: Display login form
    POST: Authenticate user and login
    """
    if request.user.is_authenticated:
        # Redirect to dashboard if already logged in
        return redirect('admissions:dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Try to authenticate with username
            user = authenticate(request, username=username, password=password)
            
            # If not found, try with email
            if not user:
                from .models import CustomUser
                try:
                    user_obj = CustomUser.objects.get(email=username)
                    user = authenticate(request, username=user_obj.username, password=password)
                except CustomUser.DoesNotExist:
                    user = None
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                
                # Redirect to next URL if provided, otherwise dashboard
                next_url = request.GET.get('next', 'admissions:dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username/email or password.')
    else:
        form = LoginForm()
    
    context = {
        'form': form,
        'page_title': 'Login',
    }
    return render(request, 'accounts/login.html', context)


@login_required(login_url='accounts:login')
@require_http_methods(['POST'])
def logout_view(request):
    """
    Handle user logout.
    """
    username = request.user.get_full_name() or request.user.username
    logout(request)
    messages.success(request, f'Goodbye, {username}! You have been logged out.')
    return redirect('accounts:login')
