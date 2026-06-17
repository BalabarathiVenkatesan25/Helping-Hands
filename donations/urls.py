from django.urls import path
from . import views

urlpatterns = [
    # Requests URLs
    path('requests/', views.request_list, name='request_list'),
    path('requests/create/', views.request_create, name='request_create'),
    path('requests/<int:request_id>/', views.request_detail, name='request_detail'),
    path('requests/<int:request_id>/edit/', views.request_edit, name='request_edit'),
    path('requests/<int:request_id>/delete/', views.request_delete, name='request_delete'),
    
    # Orphanages URLs
    path('orphanages/', views.orphanage_list, name='orphanage_list'),
    path('orphanages/<int:orphanage_id>/', views.orphanage_detail, name='orphanage_detail'),
    
    # Donation Flow
    path('requests/<int:request_id>/donate-items/', views.donate_items, name='donate_items'),
    path('requests/<int:request_id>/donate-money/', views.donate_money, name='donate_money_request'),
    path('donate-money/', views.donate_money, name='donate_money_general'),
    path('donations/<int:donation_id>/update-status/', views.update_donation_status, name='update_donation_status'),
    
    # Interactive AJAX URLs
    path('orphanages/<int:orphanage_id>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('orphanages/<int:orphanage_id>/submit-review/', views.submit_review, name='submit_review'),
]
