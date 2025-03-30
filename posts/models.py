from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    image = models.ImageField(upload_to="post_images/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    
    # Many-to-Many relationships
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)
    saved_by = models.ManyToManyField(User, related_name="saved_posts", blank=True)

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
