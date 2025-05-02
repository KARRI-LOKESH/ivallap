from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
User = get_user_model()

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    image = models.ImageField(upload_to="post_images/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    video = models.FileField(upload_to="posts/videos/", blank=True, null=True)
    # Many-to-Many relationships
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)
    saved_by = models.ManyToManyField(User, related_name="saved_posts", blank=True)
    shared_by = models.ManyToManyField(User, related_name='shared_by_posts', blank=True)
    shared_with = models.ManyToManyField(get_user_model(), related_name='shared_with_posts', blank=True)
    class Meta:
        ordering = ["-created_at"]  # Show latest posts first
        verbose_name_plural = "Posts"

    def total_likes(self):
        """Return total number of likes on a post."""
        return self.likes.count()

    def total_saves(self):
        """Return total number of times the post has been saved."""
        return self.saved_by.count()

    def __str__(self):
        return f"Post {self.id} by {self.user.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]  # Show latest comments first
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comment {self.id} by {self.user.name} on Post {self.post.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender} to {self.receiver}"
class SharedPost(models.Model):
    original_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='shared_post')
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE)
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_shared_posts')
    shared_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Shared by {self.shared_by} to {self.shared_with}"
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('like_post', 'liked your post'),
        ('like_story', 'liked your story'),
        ('comment', 'commented on your post'),
        ('follow', 'started following you'),
        ('message', 'sent you a message'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='message')
    message = models.CharField(max_length=255)
    link = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.sender.username} {self.get_notification_type_display()} to {self.user.username}"
class Story(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stories')
    media = models.FileField(upload_to='stories/', null=True, blank=True)
    caption = models.TextField(blank=True)
    is_video = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    viewers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='viewed_stories', blank=True)
    shared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='shared_stories')
    likes = models.ManyToManyField(User, related_name='story_likes', blank=True)
    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(hours=24)
    @property
    def viewer_count(self):
        return self.viewers.count()