import re
from django import template
from django.utils.safestring import mark_safe
from django.urls import reverse

register = template.Library()

@register.filter
def urlize_mentions(value):
    def replace_mention(match):
        username = match.group(1)
        url = reverse('user-profile', args=[username])
        return f'<a href="{url}" class="mention-link">@{username}</a>'

    return mark_safe(re.sub(r'@(\w+)', replace_mention, value))
