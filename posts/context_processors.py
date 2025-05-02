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
