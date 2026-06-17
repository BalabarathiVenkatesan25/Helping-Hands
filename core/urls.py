from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('contact/', views.contact, name='contact'),
    
    # Notifications URLs
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/mark-read/', views.notifications_mark_read, name='notifications_mark_read_all'),
    path('notifications/mark-read/<int:notif_id>/', views.notifications_mark_read, name='notifications_mark_read'),
    
    # Admin Reports & Messages
    path('admin/messages/', views.admin_messages_list, name='admin_messages'),
    path('reports/export/<str:report_type>/<str:export_format>/', views.export_report, name='export_report'),
    
    # Chart.js Analytics API URLs
    path('analytics/admin/', views.analytics_admin_json, name='analytics_admin_json'),
    path('analytics/orphanage/', views.analytics_orphanage_json, name='analytics_orphanage_json'),
    path('analytics/donor/', views.analytics_donor_json, name='analytics_donor_json'),
]
