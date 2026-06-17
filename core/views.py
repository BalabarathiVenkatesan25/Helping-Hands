from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.db.models import Sum, Count, Q
from django.db.models.functions import ExtractMonth
from django.utils import timezone
from datetime import datetime, timedelta

from accounts.models import User, DonorProfile, OrphanageProfile, Review
from donations.models import DonationRequest, Donation, Category
from .models import Notification, ContactMessage
from .reports import generate_pdf_report, generate_excel_report

# 1. Home Page & Contact Page
def index(request):
    # Statistics counts
    total_donors = DonorProfile.objects.count()
    total_orphanages = OrphanageProfile.objects.filter(is_approved=True).count()
    
    # Total donation calculations
    total_donations_count = Donation.objects.filter(status='Completed').count()
    completed_deliveries = Donation.objects.filter(status='Completed', donation_type='Items').count()
    
    # Featured/urgent requests (Priority high/urgent, status Open)
    featured_requests = DonationRequest.objects.filter(
        status__in=['Open', 'In Progress']
    ).filter(
        priority__in=['High', 'Urgent']
    ).order_by('-created_at')[:3]
    
    # Testimonials (Moderated reviews with high ratings)
    testimonials = Review.objects.filter(is_moderated=True, rating__gte=4).order_by('-created_at')[:4]
    
    context = {
        'total_donors': total_donors,
        'total_orphanages': total_orphanages,
        'total_donations_count': total_donations_count,
        'completed_deliveries': completed_deliveries,
        'featured_requests': featured_requests,
        'testimonials': testimonials,
    }
    return render(request, 'core/index.html', context)

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        
        # Notify superusers
        admins = User.objects.filter(is_superuser=True)
        for adm in admins:
            Notification.objects.create(
                recipient=adm,
                title="New Contact Message",
                message=f"You received a new message from {name} ({email}) regarding '{subject}'.",
                notification_type="Info"
            )

        messages.success(request, "Your message has been sent successfully. Thank you for reaching out!")
        return redirect('contact')
        
    return render(request, 'core/contact.html')

# 2. Notification Center
@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(recipient=request.user)
    return render(request, 'core/notifications.html', {'notifications_list': notifications})

@login_required
def notifications_mark_read(request, notif_id=None):
    if notif_id:
        notif = get_object_or_404(Notification, id=notif_id, recipient=request.user)
        notif.is_read = True
        notif.save()
        return JsonResponse({'status': 'success', 'unread_count': Notification.objects.filter(recipient=request.user, is_read=False).count()})
    else:
        # Mark all as read
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'unread_count': 0})
        messages.success(request, "All notifications marked as read.")
        return redirect('notifications_list')

# 3. Reports Export View (Admin Only)
def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def export_report(request, report_type, export_format):
    if export_format == 'pdf':
        pdf_data = generate_pdf_report(report_type)
        if pdf_data is None:
            return HttpResponse("Invalid report type.", status=400)
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{report_type}_report.pdf"'
        return response
    elif export_format == 'excel':
        excel_data = generate_excel_report(report_type)
        if excel_data is None:
            return HttpResponse("Invalid report type.", status=400)
        response = HttpResponse(excel_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{report_type}_report.xlsx"'
        return response
    return HttpResponse("Invalid format.", status=400)

@login_required
@user_passes_test(is_admin)
def admin_messages_list(request):
    messages_list = ContactMessage.objects.all()
    # Mark messages as read when viewed
    ContactMessage.objects.filter(is_read=False).update(is_read=True)
    return render(request, 'core/admin_messages.html', {'messages_list': messages_list})

# 4. JSON Analytics APIs for Chart.js
@login_required
def analytics_admin_json(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
        
    # a. Donations by Category
    categories = Category.objects.annotate(
        total_donated=Count('requests__donations', filter=Q(requests__donations__status='Completed'))
    )
    cat_labels = [c.name for c in categories]
    cat_data = [c.total_donated for c in categories]
    
    # b. Monthly Donations (past 6 months)
    today = timezone.now()
    six_months_ago = today - timedelta(days=180)
    monthly_donations = Donation.objects.filter(
        status='Completed',
        created_at__gte=six_months_ago
    ).annotate(
        month=ExtractMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_labels = []
    monthly_data = []
    
    # Re-map month digits to names
    for md in monthly_donations:
        monthly_labels.append(month_names[md['month'] - 1])
        monthly_data.append(md['count'])
        
    # c. User Growth (Users registered per month in current year)
    users_growth = User.objects.filter(
        date_joined__year=today.year
    ).annotate(
        month=ExtractMonth('date_joined')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    growth_labels = []
    growth_data = []
    for ug in users_growth:
        growth_labels.append(month_names[ug['month'] - 1])
        growth_data.append(ug['count'])
        
    # d. Request Completion Rate (Open vs In Progress vs Completed)
    req_status = DonationRequest.objects.values('status').annotate(count=Count('id'))
    status_labels = [s['status'] for s in req_status]
    status_data = [s['count'] for s in req_status]
    
    return JsonResponse({
        'categories': {'labels': cat_labels, 'data': cat_data},
        'monthly': {'labels': monthly_labels, 'data': monthly_data},
        'growth': {'labels': growth_labels, 'data': growth_data},
        'requests': {'labels': status_labels, 'data': status_data}
    })

@login_required
def analytics_orphanage_json(request):
    if not request.user.is_orphanage:
        return HttpResponseForbidden()
    orphanage = request.user.orphanage_profile
    
    # a. Requests Created by Month
    today = timezone.now()
    six_months_ago = today - timedelta(days=180)
    requests = DonationRequest.objects.filter(
        orphanage=orphanage,
        created_at__gte=six_months_ago
    ).annotate(
        month=ExtractMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    req_labels = []
    req_data = []
    for r in requests:
        req_labels.append(month_names[r['month'] - 1])
        req_data.append(r['count'])
        
    # b. Donations Received (Monthly count)
    donations = Donation.objects.filter(
        request__orphanage=orphanage,
        status='Completed',
        created_at__gte=six_months_ago
    ).annotate(
        month=ExtractMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    don_labels = []
    don_data = []
    for d in donations:
        don_labels.append(month_names[d['month'] - 1])
        don_data.append(d['count'])
        
    # c. Monthly Fulfillment rates
    # Return count of open requests vs completed requests
    open_reqs = DonationRequest.objects.filter(orphanage=orphanage, status__in=['Open', 'In Progress']).count()
    comp_reqs = DonationRequest.objects.filter(orphanage=orphanage, status='Completed').count()
    
    return JsonResponse({
        'requests': {'labels': req_labels, 'data': req_data},
        'donations': {'labels': don_labels, 'data': don_data},
        'fulfillment': {'labels': ['Active Requests', 'Completed Requests'], 'data': [open_reqs, comp_reqs]}
    })

@login_required
def analytics_donor_json(request):
    if not request.user.is_donor:
        return HttpResponseForbidden()
    donor = request.user.donor_profile
    
    # a. Donation History (Past 6 months completed counts)
    today = timezone.now()
    six_months_ago = today - timedelta(days=180)
    my_donations = Donation.objects.filter(
        donor=donor,
        status='Completed',
        created_at__gte=six_months_ago
    ).annotate(
        month=ExtractMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    don_labels = []
    don_data = []
    for d in my_donations:
        don_labels.append(month_names[d['month'] - 1])
        don_data.append(d['count'])
        
    # b. Donation Categories (Where did they donate)
    categories = Category.objects.filter(
        requests__donations__donor=donor,
        requests__donations__status='Completed'
    ).annotate(
        count=Count('requests__donations')
    )
    cat_labels = [c.name for c in categories]
    cat_data = [c.count for c in categories]
    
    return JsonResponse({
        'donations': {'labels': don_labels, 'data': don_data},
        'categories': {'labels': cat_labels, 'data': cat_data}
    })

# 5. Custom Error Pages
def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)
