
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from cloudinary.models import CloudinaryField
User = get_user_model()

class Post(models.Model):
    FILTER_CHOICES = [
    ('none', 'Normal'),
    ('contrast(130%) brightness(110%) saturate(180%)', 'Vibrant Pop'),
    ('sepia(40%) contrast(120%) brightness(105%)', 'Warm Glow'),
    ('grayscale(80%) contrast(140%) brightness(90%)', 'Moody B&W'),
    ('drop-shadow(8px 8px 6px rgba(0,0,0,0.5)) brightness(110%)', 'Shadow Glow'),
    ('hue-rotate(180deg) saturate(150%) brightness(90%)', 'Cool Tone'),
    ('brightness(90%) contrast(140%) saturate(150%) sepia(30%)', 'Retro Warmth'),
    ('brightness(110%) contrast(120%) blur(1px)', 'Dreamy Soft'),
    ('contrast(160%) saturate(200%) brightness(115%)', 'Ultra Vivid'),
    ('sepia(100%) contrast(150%) brightness(85%) grayscale(20%)', 'Classic Film'),
    ('invert(20%) hue-rotate(20deg) saturate(250%)', 'Neon Glow'),
    ('brightness(150%) contrast(120%) drop-shadow(4px 4px 6px #000)', 'Radiant Light'),
    ('grayscale(100%)', 'Grayscale'),
    ('sepia(100%)', 'Sepia'),
    ('blur(2px)', 'Blur'),
    ('contrast(150%)', 'High Contrast'),
    ('brightness(120%)', 'Bright'),
    ('invert(100%)', 'Invert'),
    ('hue-rotate(90deg)', 'Hue Rotate'),
    ('saturate(200%)', 'Saturate'),
    ('drop-shadow(5px 5px 5px gray)', 'Drop Shadow')
]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    image = CloudinaryField('image',null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    video = CloudinaryField(resource_type='video', blank=True, null=True)
    filter = models.CharField(max_length=100, choices=FILTER_CHOICES, default='none')
    location = models.CharField(max_length=255, blank=True)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)
    saved_by = models.ManyToManyField(User, related_name="saved_posts", blank=True)
    shared_by = models.ManyToManyField(User, related_name='shared_by_posts', blank=True)
    shared_with = models.ManyToManyField(get_user_model(), related_name='shared_with_posts', blank=True)
    class Meta:
        ordering = ["-created_at"]  # Show latest posts first
        verbose_name_plural = "Posts"
        
    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})

    def total_likes(self):
        """Return total number of likes on a post."""
        return self.likes.count()

    def total_saves(self):
        """Return total number of times the post has been saved."""
        return self.saved_by.count()

    def __str__(self):
        return f"Post {self.id} by {self.user.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', null=True, blank=True) 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)  # Allow null initially
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    class Meta:
        ordering = ["-created_at"]
    def is_owner_liked(self, user):
        """Check if the post owner liked the comment."""
        return self.likes.filter(id=user.id).exists()
    def total_likes(self):
        return self.likes.count()
    def first_liker(self):
        """Return first user who liked the comment."""
        return self.likes.first()
    def __str__(self):
        return f"Comment {self.id} by {self.user.username} on {self.content_type} {self.object_id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
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
    related_request = models.ForeignKey('users.FollowRequest', on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return f"{self.sender.username} {self.get_notification_type_display()} to {self.user.username}"
class Story(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stories')
    media = CloudinaryField('media',null=True, blank=True)
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
    
class Reel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    video = CloudinaryField(resource_type='video')
    caption = models.TextField(default="No caption")  # Default value added for caption
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_reels', blank=True)
    saved_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='saved_reels', blank=True)
    shared_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='shared_reels', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    comments = GenericRelation(Comment)
    def total_likes(self):
        return self.likes.count()
    
    def total_shares(self):
        return self.shared_by.count()
    
    def total_saves(self):
        return self.saved_by.count()

    # Add this method to check if the reel is liked by the current user
    def is_liked_by(self, user):
        return user in self.likes.all()

    def is_saved_by(self, user):
        return user in self.saved_by.all()

    def __str__(self):
        return f"Reel by {self.user.username} - {self.created_at.strftime('%Y-%m-%d')}"

    class Meta:
        ordering = ['-created_at']
class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE, related_name='reports')
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.user.username} on Reel {self.reel.id}"
