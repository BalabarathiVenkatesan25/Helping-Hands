from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone

from accounts.models import OrphanageProfile, DonorProfile, Favorite, Review
from core.models import Notification
from .models import Category, DonationRequest, Donation
from .forms import DonationRequestForm, ItemDonationForm, MoneyDonationForm
from accounts.forms import ReviewForm

# Request Views (CRUD for Orphanage)
@login_required
def request_create(request):
    if not request.user.is_orphanage:
        return redirect('dashboard')
    orphanage = request.user.orphanage_profile
    if not orphanage.is_approved:
        return redirect('pending_approval')

    if request.method == 'POST':
        form = DonationRequestForm(request.POST, request.FILES)
        if form.is_valid():
            req = form.save(commit=False)
            req.orphanage = orphanage
            req.save()
            
            # Send notification to orphanage
            Notification.objects.create(
                recipient=request.user,
                title="Donation Request Created",
                message=f"Your request '{req.title}' has been posted and is now public.",
                notification_type="Success"
            )
            
            # Notify donors who favorited this orphanage
            favorited_donors = Favorite.objects.filter(orphanage=orphanage)
            for fav in favorited_donors:
                Notification.objects.create(
                    recipient=fav.donor.user,
                    title=f"New Request from {orphanage.orphanage_name}",
                    message=f"An orphanage you favorited has published a new request: '{req.title}'.",
                    notification_type="Info"
                )

            messages.success(request, f"Request '{req.title}' has been successfully created.")
            return redirect('orphanage_dashboard')
    else:
        form = DonationRequestForm()
    return render(request, 'donations/request_form.html', {'form': form, 'title': 'Create Donation Request'})

@login_required
def request_edit(request, request_id):
    if not request.user.is_orphanage:
        return redirect('dashboard')
    req = get_object_or_404(DonationRequest, id=request_id, orphanage=request.user.orphanage_profile)
    
    if request.method == 'POST':
        form = DonationRequestForm(request.POST, request.FILES, instance=req)
        if form.is_valid():
            form.save()
            messages.success(request, f"Request '{req.title}' has been updated.")
            return redirect('orphanage_dashboard')
    else:
        form = DonationRequestForm(instance=req)
    return render(request, 'donations/request_form.html', {'form': form, 'title': 'Edit Donation Request'})

@login_required
def request_delete(request, request_id):
    if not request.user.is_orphanage:
        return redirect('dashboard')
    req = get_object_or_404(DonationRequest, id=request_id, orphanage=request.user.orphanage_profile)
    title = req.title
    req.delete()
    messages.success(request, f"Request '{title}' has been deleted.")
    return redirect('orphanage_dashboard')

# Request Details & Listing
def request_list(request):
    categories = Category.objects.all()
    # Initial list is open requests
    requests = DonationRequest.objects.filter(status__in=['Open', 'In Progress']).order_by('-created_at')
    
    # Check if AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        q = request.GET.get('q', '')
        category_slug = request.GET.get('category', '')
        priority = request.GET.get('priority', '')
        status = request.GET.get('status', '')
        location = request.GET.get('location', '')
        
        filters = Q()
        if q:
            filters &= (Q(title__icontains=q) | Q(description__icontains=q) | Q(orphanage__orphanage_name__icontains=q))
        if category_slug:
            filters &= Q(category__slug=category_slug)
        if priority:
            filters &= Q(priority=priority)
        if status:
            filters &= Q(status=status)
        else:
            # default to show active requests if no status requested
            filters &= Q(status__in=['Open', 'In Progress'])
        if location:
            filters &= Q(orphanage__address__icontains=location)
            
        requests = DonationRequest.objects.filter(filters).distinct().order_by('-created_at')
        html = render_to_string('donations/includes/request_list_items.html', {'requests': requests, 'user': request.user})
        return JsonResponse({'html': html})
        
    return render(request, 'donations/request_list.html', {'requests': requests, 'categories': categories})

def request_detail(request, request_id):
    req = get_object_or_404(DonationRequest, id=request_id)
    # Get active/completed donations for this request
    donations = req.donations.all().order_by('-created_at')
    return render(request, 'donations/request_detail.html', {'request_item': req, 'donations': donations})

# Orphanage Views
def orphanage_list(request):
    orphanages = OrphanageProfile.objects.filter(is_approved=True)
    categories = Category.objects.all()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        q = request.GET.get('q', '')
        location = request.GET.get('location', '')
        
        filters = Q(is_approved=True)
        if q:
            filters &= (Q(orphanage_name__icontains=q) | Q(description__icontains=q))
        if location:
            filters &= Q(address__icontains=location)
            
        orphanages = OrphanageProfile.objects.filter(filters).distinct()
        
        # Inject favorites if logged in
        fav_ids = []
        if request.user.is_authenticated and request.user.is_donor:
            fav_ids = Favorite.objects.filter(donor=request.user.donor_profile).values_list('orphanage_id', flat=True)
            
        html = render_to_string('donations/includes/orphanage_list_items.html', {
            'orphanages': orphanages, 
            'fav_ids': fav_ids,
            'user': request.user
        })
        return JsonResponse({'html': html})

    fav_ids = []
    if request.user.is_authenticated and request.user.is_donor:
        fav_ids = Favorite.objects.filter(donor=request.user.donor_profile).values_list('orphanage_id', flat=True)

    return render(request, 'donations/orphanage_list.html', {
        'orphanages': orphanages,
        'categories': categories,
        'fav_ids': fav_ids
    })

def orphanage_detail(request, orphanage_id):
    orphanage = get_object_or_404(OrphanageProfile, id=orphanage_id, is_approved=True)
    requests = orphanage.requests.filter(status__in=['Open', 'In Progress']).order_by('-created_at')
    reviews = orphanage.reviews.filter(is_moderated=True).order_by('-created_at')
    
    is_favorited = False
    review_form = None
    if request.user.is_authenticated and request.user.is_donor:
        is_favorited = Favorite.objects.filter(donor=request.user.donor_profile, orphanage=orphanage).exists()
        review_form = ReviewForm()

    context = {
        'orphanage': orphanage,
        'requests': requests,
        'reviews': reviews,
        'is_favorited': is_favorited,
        'review_form': review_form
    }
    return render(request, 'donations/orphanage_detail.html', context)

# Donation Flow
@login_required
def donate_items(request, request_id):
    if not request.user.is_donor:
        return HttpResponseForbidden("Only donors can make donations.")
    req = get_object_or_404(DonationRequest, id=request_id)
    if req.status == 'Completed':
        messages.error(request, "This donation request has already been completed.")
        return redirect('request_detail', request_id=request_id)

    if request.method == 'POST':
        form = ItemDonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.donor = request.user.donor_profile
            donation.request = req
            donation.donation_type = 'Items'
            donation.status = 'Pending'
            donation.save()

            # Update request status to 'In Progress'
            if req.status == 'Open':
                req.status = 'In Progress'
                req.save()

            # Notify Orphanage
            Notification.objects.create(
                recipient=req.orphanage.user,
                title="New Donation Received",
                message=f"{donation.donor.full_name} has offered to donate {donation.quantity_donated} items for request '{req.title}'. Check your dashboard to accept.",
                notification_type="Info"
            )

            messages.success(request, f"Thank you! Your donation offer for '{req.title}' has been submitted. The orphanage has been notified.")
            return redirect('donor_dashboard')
    else:
        form = ItemDonationForm()
    return render(request, 'donations/donate_items.html', {'form': form, 'request_item': req})

@login_required
def donate_money(request, request_id=None):
    if not request.user.is_donor:
        return HttpResponseForbidden("Only donors can make donations.")
    
    req = None
    if request_id:
        req = get_object_or_404(DonationRequest, id=request_id)
        if req.status == 'Completed':
            messages.error(request, "This donation request has already been completed.")
            return redirect('request_detail', request_id=request_id)

    if request.method == 'POST':
        form = MoneyDonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.donor = request.user.donor_profile
            donation.request = req
            donation.donation_type = 'Money'
            donation.status = 'Pending' # Starts pending until orphanage confirms or auto-confirms simulation
            donation.save()

            # For simulated money, let's auto-accept it or keep it pending for orphanage to accept.
            # Let's keep it pending so orphanages can review and mark 'Completed' to receive the donation.
            if req and req.status == 'Open':
                req.status = 'In Progress'
                req.save()

            # Notify Orphanage
            Notification.objects.create(
                recipient=req.orphanage.user if req else User.objects.filter(is_superuser=True).first(),
                title="New Money Donation Offered",
                message=f"{donation.donor.full_name} has donated ${donation.amount} simulated money. Verify and accept this donation in your dashboard.",
                notification_type="Info"
            )

            messages.success(request, "Simulated payment transaction successful! The donation is registered and pending review.")
            return redirect('donor_dashboard')
    else:
        form = MoneyDonationForm()
    return render(request, 'donations/donate_money.html', {'form': form, 'request_item': req})

# Orphanage Actions
@login_required
def update_donation_status(request, donation_id):
    if not request.user.is_orphanage:
        return HttpResponseForbidden()
    donation = get_object_or_404(Donation, id=donation_id, request__orphanage=request.user.orphanage_profile)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Donation.STATUS_CHOICES):
            donation.status = new_status
            donation.save()
            
            # Send Notification to Donor
            Notification.objects.create(
                recipient=donation.donor.user,
                title="Donation Status Updated",
                message=f"Your donation status has been updated to '{new_status}' by {request.user.orphanage_profile.orphanage_name}.",
                notification_type="Info"
            )
            
            # If marked completed, trigger request quantity update
            if new_status == 'Completed':
                req = donation.request
                if req:
                    if donation.donation_type == 'Items':
                        req.quantity_fulfilled += donation.quantity_donated
                    # check if fully met
                    if req.quantity_fulfilled >= req.quantity_needed:
                        req.status = 'Completed'
                    req.save()
                    
                    # Notify donor
                    Notification.objects.create(
                        recipient=donation.donor.user,
                        title="Donation Completed successfully",
                        message=f"Thank you! Your donation for '{req.title}' has been successfully completed and received.",
                        notification_type="Success"
                    )
                    
            messages.success(request, f"Donation status updated to {new_status}.")
            return redirect('orphanage_dashboard')
            
    messages.error(request, "Invalid request.")
    return redirect('orphanage_dashboard')

# Favorite Action (AJAX)
@login_required
def toggle_favorite(request, orphanage_id):
    if not request.user.is_donor:
        return JsonResponse({'error': 'Only donors can favorite orphanages.'}, status=403)
    
    orphanage = get_object_or_404(OrphanageProfile, id=orphanage_id)
    donor = request.user.donor_profile
    
    favorite, created = Favorite.objects.get_or_create(donor=donor, orphanage=orphanage)
    if not created:
        favorite.delete()
        is_fav = False
        message = f"Removed {orphanage.orphanage_name} from favorites."
    else:
        is_fav = True
        message = f"Added {orphanage.orphanage_name} to favorites."
        
    return JsonResponse({'is_favorited': is_fav, 'message': message})

# Review Submission
@login_required
def submit_review(request, orphanage_id):
    if not request.user.is_donor:
        return HttpResponseForbidden()
    orphanage = get_object_or_404(OrphanageProfile, id=orphanage_id)
    donor = request.user.donor_profile
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.donor = donor
            review.orphanage = orphanage
            # Review is held for admin moderation
            review.is_moderated = False
            review.save()
            
            # Notify admins of new review to moderate
            admins = User.objects.filter(is_superuser=True)
            for adm in admins:
                Notification.objects.create(
                    recipient=adm,
                    title="New Review Pending Moderation",
                    message=f"Donor {donor.full_name} left a review for {orphanage.orphanage_name} which requires your moderation.",
                    notification_type="Info"
                )

            messages.info(request, "Feedback submitted successfully! It will be published after administrator approval.")
            return redirect('orphanage_detail', orphanage_id=orphanage_id)
            
    messages.error(request, "Failed to submit review. Please check the values.")
    return redirect('orphanage_detail', orphanage_id=orphanage_id)
