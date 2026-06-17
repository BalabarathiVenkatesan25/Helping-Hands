from core.models import Notification

def notification_context(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(recipient=request.user, is_read=False)
        return {
            'unread_notifications_count': notifications.count(),
            'unread_notifications': notifications[:5]
        }
    return {
        'unread_notifications_count': 0,
        'unread_notifications': []
    }
