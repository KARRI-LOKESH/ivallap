from django.utils import timezone
from .models import Story

def get_recent_stories(request):
    if request.user.is_authenticated:
        recent_stories = Story.objects.filter(
            created_at__gte=timezone.now() - timezone.timedelta(hours=24)
        ).order_by('-created_at')

        unique_stories = {}
        for story in recent_stories:
            if story.user not in unique_stories:
                unique_stories[story.user] = story

        return {'stories': unique_stories.values()}
    return {'stories': []}
from .models import Notification

def notification_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
    else:
        count = 0
    return {'notification_count': count}
from .models import Message

def unread_messages_count(request):
    if request.user.is_authenticated:
        count = Message.objects.filter(receiver=request.user, is_read=False).count()
        return {'unread_message_count': count}
    return {}
