from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta

from .models import User, DonorProfile, OrphanageProfile, Review, Favorite
from donations.models import DonationRequest, Donation, Category
from core.models import Notification, ContactMessage
from .forms import (
    DonorRegistrationForm,
    OrphanageRegistrationForm,
    DonorProfileForm,
    OrphanageProfileForm,
    UserEmailForm,
    ReviewForm
)

def is_admin(user):
    return user.is_superuser

# Authentication Views
def register_donor(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome to Helping Hands.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DonorRegistrationForm()
    return render(request, 'accounts/register_donor.html', {'form': form})

def register_orphanage(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = OrphanageRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # We don't log them in yet, or if we do, the middleware redirects to pending_approval.
            # Let's log them in and let the middleware redirect to pending_approval.
            login(request, user)
            messages.info(request, "Registration submitted! Your profile is pending administrator approval.")
            return redirect('pending_approval')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = OrphanageRegistrationForm()
    return render(request, 'accounts/register_orphanage.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        passw = request.POST.get('password')
        user = authenticate(request, username=username, password=passw)
        if user is not None:
            if not user.is_active:
                messages.error(request, "Your account has been suspended. Please contact the administrator.")
                return render(request, 'accounts/login.html')
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "You have logged out successfully.")
    return redirect('index')

def pending_approval(request):
    if not request.user.is_authenticated or not request.user.is_orphanage:
        return redirect('index')
    # Check if they became approved in the meantime
    profile = getattr(request.user, 'orphanage_profile', None)
    if profile and profile.is_approved:
        return redirect('dashboard')
    return render(request, 'accounts/pending_approval.html', {'profile': profile})

# Dashboard Redirect Router
@login_required
def dashboard_router(request):
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    elif request.user.is_donor:
        return redirect('donor_dashboard')
    elif request.user.is_orphanage:
        profile = getattr(request.user, 'orphanage_profile', None)
        if profile and profile.is_approved:
            return redirect('orphanage_dashboard')
        else:
            return redirect('pending_approval')
    return redirect('index')

# Dashboards views
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Metrics
    total_donors = DonorProfile.objects.count()
    total_orphanages = OrphanageProfile.objects.count()
    pending_orphanages = OrphanageProfile.objects.filter(is_approved=False)
    total_requests = DonationRequest.objects.count()
    
    total_donations_value = Donation.objects.filter(status='Completed', donation_type='Money').aggregate(Sum('amount'))['amount__avg'] or 0.00
    # Let's count items and money
    total_item_donations = Donation.objects.filter(status='Completed', donation_type='Items').count()
    total_money_donations = Donation.objects.filter(status='Completed', donation_type='Money').count()
    
    # Recent users/requests
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_requests = DonationRequest.objects.order_by('-created_at')[:5]
    recent_donations = Donation.objects.order_by('-created_at')[:5]
    
    # Categories for management
    categories = Category.objects.all()
    
    # Reviews for moderation
    pending_reviews = Review.objects.filter(is_moderated=False)
    
    context = {
        'total_donors': total_donors,
        'total_orphanages': total_orphanages,
        'pending_orphanages': pending_orphanages,
        'total_requests': total_requests,
        'total_item_donations': total_item_donations,
        'total_money_donations': total_money_donations,
        'recent_users': recent_users,
        'recent_requests': recent_requests,
        'recent_donations': recent_donations,
        'categories': categories,
        'pending_reviews': pending_reviews,
    }
    return render(request, 'accounts/dashboard_admin.html', context)

@login_required
def donor_dashboard(request):
    if not request.user.is_donor:
        return redirect('dashboard')
    donor = request.user.donor_profile
    
    # Donor metrics
    donations = Donation.objects.filter(donor=donor)
    total_donations = donations.count()
    active_donations = donations.exclude(status='Completed').count()
    completed_donations = donations.filter(status='Completed').count()
    
    recent_donations = donations.order_by('-created_at')[:5]
    favorites = Favorite.objects.filter(donor=donor)[:5]
    
    # Activity log: notifications or donations
    recent_notifications = Notification.objects.filter(recipient=request.user)[:5]

    context = {
        'donor': donor,
        'total_donations': total_donations,
        'active_donations': active_donations,
        'completed_donations': completed_donations,
        'recent_donations': recent_donations,
        'favorites': favorites,
        'recent_notifications': recent_notifications
    }
    return render(request, 'accounts/dashboard_donor.html', context)

@login_required
def orphanage_dashboard(request):
    if not request.user.is_orphanage:
        return redirect('dashboard')
    orphanage = request.user.orphanage_profile
    if not orphanage.is_approved:
        return redirect('pending_approval')
        
    requests = DonationRequest.objects.filter(orphanage=orphanage)
    total_requests = requests.count()
    pending_requests = requests.filter(status='Open').count()
    in_progress_requests = requests.filter(status='In Progress').count()
    completed_requests = requests.filter(status='Completed').count()
    
    recent_donations = Donation.objects.filter(request__orphanage=orphanage).order_by('-created_at')[:5]
    my_requests = requests.order_by('-created_at')[:5]
    
    context = {
        'orphanage': orphanage,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'in_progress_requests': in_progress_requests,
        'completed_requests': completed_requests,
        'recent_donations': recent_donations,
        'my_requests': my_requests
    }
    return render(request, 'accounts/dashboard_orphanage.html', context)

# Profile Management
@login_required
def profile_view(request):
    user = request.user
    password_form = PasswordChangeForm(user)
    
    if user.is_donor:
        profile = user.donor_profile
        profile_form = DonorProfileForm(instance=profile)
        email_form = UserEmailForm(instance=user)
    elif user.is_orphanage:
        profile = user.orphanage_profile
        profile_form = OrphanageProfileForm(instance=profile)
        email_form = UserEmailForm(instance=user)
    else:
        profile = None
        profile_form = None
        email_form = UserEmailForm(instance=user)
        
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_profile':
            email_form = UserEmailForm(request.POST, instance=user)
            if profile_form:
                if user.is_donor:
                    profile_form = DonorProfileForm(request.POST, request.FILES, instance=profile)
                else:
                    profile_form = OrphanageProfileForm(request.POST, request.FILES, instance=profile)
            
            if email_form.is_valid() and (profile_form is None or profile_form.is_valid()):
                email_form.save()
                if profile_form:
                    profile_form.save()
                messages.success(request, "Your profile has been updated successfully.")
                return redirect('profile')
            else:
                messages.error(request, "Failed to update profile. Please verify your fields.")
                
        elif action == 'change_password':
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user) # keep logged in
                messages.success(request, "Your password has been changed successfully.")
                return redirect('profile')
            else:
                messages.error(request, "Failed to change password. Please check requirements.")
                
    # Calculate profile completion percentage
    completion = 0
    if user.is_donor:
        fields = [profile.full_name, profile.phone_number, profile.address, profile.profile_picture]
        filled = sum(1 for f in fields if f)
        completion = int((filled / len(fields)) * 100)
    elif user.is_orphanage:
        fields = [profile.orphanage_name, profile.phone, profile.address, profile.description, profile.profile_image]
        filled = sum(1 for f in fields if f)
        completion = int((filled / len(fields)) * 100)
    else:
        completion = 100
        
    context = {
        'profile_form': profile_form,
        'email_form': email_form,
        'password_form': password_form,
        'completion_percentage': completion,
    }
    return render(request, 'accounts/profile.html', context)

# Admin Operations
@login_required
@user_passes_test(is_admin)
def admin_toggle_approval(request, profile_id):
    profile = get_object_or_404(OrphanageProfile, id=profile_id)
    profile.is_approved = not profile.is_approved
    profile.save()
    
    # Notify user
    status_str = "approved" if profile.is_approved else "rejected"
    Notification.objects.create(
        recipient=profile.user,
        title="Orphanage Registration Status Update",
        message=f"Your registration for '{profile.orphanage_name}' has been {status_str} by the administrator.",
        notification_type="Success" if profile.is_approved else "Warning"
    )
    
    messages.success(request, f"Orphanage '{profile.orphanage_name}' approval status updated.")
    return redirect('admin_dashboard')

@login_required
@user_passes_test(is_admin)
def admin_toggle_suspension(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_superuser:
        messages.error(request, "Cannot suspend the super administrator.")
        return redirect('admin_users_list')
        
    user.is_active = not user.is_active
    user.save()
    
    status_str = "activated" if user.is_active else "suspended"
    messages.success(request, f"User {user.username} has been successfully {status_str}.")
    return redirect('admin_users_list')

@login_required
@user_passes_test(is_admin)
def admin_users_list(request):
    donors = DonorProfile.objects.all()
    orphanages = OrphanageProfile.objects.all()
    return render(request, 'accounts/admin_users_list.html', {'donors': donors, 'orphanages': orphanages})

# Review & Feedback management
@login_required
@user_passes_test(is_admin)
def admin_review_moderate(request, review_id, action):
    review = get_object_or_404(Review, id=review_id)
    if action == 'approve':
        review.is_moderated = True
        review.save()
        messages.success(request, "Review has been approved and published.")
    elif action == 'delete':
        review.delete()
        messages.success(request, "Review has been successfully deleted.")
    return redirect('admin_dashboard')
