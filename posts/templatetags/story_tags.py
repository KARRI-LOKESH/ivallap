from django import template
from posts.models import Story
from django.utils import timezone

register = template.Library()

@register.filter
def has_active_story(user):
    if not user.is_authenticated:
        return False
    return Story.objects.filter(user=user, created_at__gte=timezone.now() - timezone.timedelta(hours=24)).exists()
