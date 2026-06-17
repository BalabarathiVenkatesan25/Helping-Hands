from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/donor/', views.register_donor, name='register_donor'),
    path('register/orphanage/', views.register_orphanage, name='register_orphanage'),
    path('pending-approval/', views.pending_approval, name='pending_approval'),
    path('dashboard/', views.dashboard_router, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    
    # Specific Dashboards
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/donor/', views.donor_dashboard, name='donor_dashboard'),
    path('dashboard/orphanage/', views.orphanage_dashboard, name='orphanage_dashboard'),
    
    # Admin Controls
    path('admin/toggle-approval/<int:profile_id>/', views.admin_toggle_approval, name='admin_toggle_approval'),
    path('admin/toggle-suspension/<int:user_id>/', views.admin_toggle_suspension, name='admin_toggle_suspension'),
    path('admin/users/', views.admin_users_list, name='admin_users_list'),
    path('admin/review-moderate/<int:review_id>/<str:action>/', views.admin_review_moderate, name='admin_review_moderate'),
]
