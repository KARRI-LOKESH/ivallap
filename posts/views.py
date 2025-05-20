from django.shortcuts import render, get_object_or_404, redirect,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy,reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Post, Comment,Message,SharedPost,Notification,Story,Reel
from users.models import CustomUser
from posts.forms import MessageForm,StoryUploadForm,CommentForm,PostForm
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.utils.timezone import localtime
import json
import re
import cloudinary.uploader
from django.core.files.base import ContentFile
import base64
from django.views.decorators.csrf import csrf_exempt
from cloudinary.uploader import upload
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.http import JsonResponse # Ensure Post model is imported
from django.contrib.auth import get_user_model

class PostListView(ListView):
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_urls = {
            post.pk: self.request.build_absolute_uri(post.get_absolute_url())
            for post in context['posts']
        }
        context['post_urls'] = post_urls
        return context
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'
    success_url = reverse_lazy('post-list')

    def form_valid(self, form):
        image = self.request.FILES.get('image')
        video = self.request.FILES.get('video')
        cropped_data = self.request.POST.get('cropped_image')
        selected_filter = self.request.POST.get('filter', 'none')

        # Prevent both image and video upload simultaneously
        if image and video:
            form.add_error('video', "You can't upload both an image and a video in the same post.")
            return self.form_invalid(form)

        # Validate image type if provided
        if image and not image.content_type.startswith('image/'):
            form.add_error('image', 'Uploaded file is not a valid image.')
            return self.form_invalid(form)

        # Validate video type if provided
        if video and not video.content_type.startswith('video/'):
            form.add_error('video', 'Uploaded file is not a valid video.')
            return self.form_invalid(form)

        form.instance.user = self.request.user
        form.instance.filter = selected_filter or 'none'

        # Save form without commit
        instance = form.save(commit=False)

        if cropped_data:
            try:
                format, imgstr = cropped_data.split(';base64,')
                ext = format.split('/')[-1]
                # Decode base64 image to bytes
                img_bytes = base64.b64decode(imgstr)

                # Upload directly to Cloudinary
                upload_result = cloudinary.uploader.upload(
                    img_bytes,
                    folder="your_folder_name",  # optional
                    resource_type="image",
                    public_id=None,
                    overwrite=True,
                )
                # Assign the Cloudinary public_id or URL to the CloudinaryField
                instance.image = upload_result['public_id']
            except Exception as e:
                form.add_error('image', f'Error uploading cropped image: {e}')
                return self.form_invalid(form)
        else:
            if image:
                # Directly assign uploaded file (this will be handled by CloudinaryField storage)
                instance.image = image

        instance.save()

        if video:
            reel = Reel(user=self.request.user, video=video, caption=form.cleaned_data.get('content'))
            reel.save()
            messages.success(self.request, "Reel uploaded successfully.")
            return redirect('reel-list')

        messages.success(self.request, "Post created successfully.")
        return redirect(self.success_url)
class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object

        post_type = ContentType.objects.get_for_model(Post)
        comments = Comment.objects.filter(
            content_type=post_type,
            object_id=post.id
        )

        context['post'] = post
        context['comments'] = comments

        return context

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['content', 'video', 'filter', 'location']
    template_name = 'posts/post_form.html'
    success_url = reverse_lazy('post-list')

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)

    def form_valid(self, form):
        cropped_data = self.request.POST.get('cropped_image')
        instance = form.save(commit=False)

        if cropped_data:
            try:
                format, imgstr = cropped_data.split(';base64,')
                ext = format.split('/')[-1]
                img_bytes = base64.b64decode(imgstr)

                # Upload to Cloudinary
                upload_result = cloudinary.uploader.upload(
                    img_bytes,
                    folder="post_images",  # optional
                    resource_type="image",
                    overwrite=True,
                )
                instance.image = upload_result['public_id']
            except Exception as e:
                form.add_error('image', f'Error uploading cropped image: {e}')
                return self.form_invalid(form)

        instance.save()
        messages.success(self.request, "Post updated successfully.")
        return redirect(self.success_url)
class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'posts/post_confirm_delete.html'
    success_url = reverse_lazy('post-list')

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)

@login_required
def like_post(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)

        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True

            # Create a notification
            if post.user != request.user:  # avoid self-notification
                Notification.objects.create(
                    user=post.user,
                    sender=request.user,
                    notification_type='like_post',
                    post=post,
                    message=f"{request.user.username} liked your post!",
                    link=f"/post/{post.id}/"
                )

        return JsonResponse({"liked": liked, "total_likes": post.likes.count()})

    return JsonResponse({"error": "Invalid request"}, status=400)
@login_required
def save_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user in post.saved_by.all():
        post.saved_by.remove(request.user)
        saved = False
    else:
        post.saved_by.add(request.user)
        saved = True

    return JsonResponse({
        "total_saves": post.saved_by.count(),
        "saved": saved
    })

User = get_user_model()

@login_required
def share_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        shared_with_username = request.POST.get('shared_with', '').strip()
        share_with_self = request.POST.get('share_with_self')
        shared_any = False

        # Share with another user (case-insensitive)
        if shared_with_username:
            try:
                user_to_share_with = User.objects.get(username__iexact=shared_with_username)
                if user_to_share_with != request.user:
                    post.shared_with.add(user_to_share_with)
                    Notification.objects.create(
                        user=user_to_share_with,
                        message=f"{request.user.username} shared a <a href='{reverse('post-detail', kwargs={'pk': post.id})}'>post</a> with you!"
                    )
                    shared_any = True
                else:
                    messages.warning(request, "You cannot share a post with yourself using username. Select 'Share to my profile' instead.")
            except User.DoesNotExist:
                messages.error(request, "User not found.")
                return redirect("post-detail", pk=post_id)

        # Share with self
        if share_with_self:
            post.shared_with.add(request.user)
            Notification.objects.create(
                user=request.user,
                message="You shared a post to your profile."
            )
            shared_any = True

        if shared_any:
            messages.success(request, "Post shared successfully.")
        else:
            messages.warning(request, "No one selected to share the post.")

        return redirect("post-detail", pk=post_id)

    return redirect("post-list")
User = get_user_model()

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            comment = Comment.objects.create(user=request.user, post=post, content=content)
            print(f"New Comment Added by {comment.user}: {comment.content}")

            # Create a notification to the post owner
            if post.user != request.user:  # avoid self-notifications
                Notification.objects.create(
                    user=post.user,
                    sender=request.user,
                    notification_type='comment',
                    post=post,
                    message=f"{request.user.username} commented on your post!",
                    link=f"/post/{post.id}/"
                )

            # ✅ Handle @mentions
            mentions = re.findall(r'@(\w+)', content)
            for username in mentions:
                try:
                    mentioned_user = User.objects.get(username=username)
                    if mentioned_user != request.user:
                        Notification.objects.create(
                            user=mentioned_user,
                            sender=request.user,
                            notification_type='mention',
                            post=post,
                            message=f"{request.user.username} mentioned you in a comment.",
                            link=f"post/{post.id}/"
                        )
                except User.DoesNotExist:
                    pass  # Ignore mentions of non-existent users

    return redirect('post-detail', pk=post.id)
 # Redirect to the same post

@login_required(login_url='entry')  # Redirects to entry.html if not logged in
def dashboard(request):
    return render(request, 'users/entry.html')
def send_message(request):
    return render(request, 'posts/send_message.html')
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post = comment.post  # Get the related post

    print(f"Deleting comment {comment_id} from post {post.id}")
    print(f"Comment Owner: {comment.user}, Post Owner: {post.user}, Logged-in User: {request.user}")

    if request.user == comment.user or request.user == post.user:  
        comment.delete()
        print("Comment deleted successfully.")
    else:
        print("User not authorized to delete this comment.")

    return redirect('post-list')
User = get_user_model()
@login_required
def send_message(request, receiver_id):
    receiver = get_object_or_404(User, id=receiver_id)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = receiver
            message.save()

            # Notification creation
            if receiver != request.user:
                Notification.objects.create(
                    user=receiver,
                    sender=request.user,
                    notification_type='message',
                    message=f"{request.user.username} sent you a message!",
                    link=f"/messages/{receiver.username}/"
                )

            return redirect('inbox')
    else:
        form = MessageForm()

    return render(request, 'posts/send_message.html', {
        'form': form,
        'receiver': receiver
    })
@login_required
def inbox(request):
    received_messages = Message.objects.filter(receiver=request.user).order_by('-timestamp')
    # ✅ Mark messages as read
    Message.objects.filter(receiver=request.user, is_read=False).update(is_read=True)
    return render(request, 'posts/inbox.html', {
        'messages': received_messages
    })

@login_required
def chat_view(request, username):
    return render(request, 'posts/chat.html', {
        'username': username,
        'room_name': request.user.id  # or use a room ID logic
    })

@login_required
def notifications_view(request):
    notifications = request.user.notifications.all().order_by('-timestamp')
    # Optional: Mark all notifications as read
    notifications.update(is_read=True)
    return render(request, 'posts/notifications.html', {'notifications': notifications})
from cloudinary.uploader import upload

@login_required
def upload_story(request):
    if request.method == 'POST':
        media = request.FILES.get('media')
        caption = request.POST.get('caption', '')

        if not media:
            messages.error(request, "Please select a media file.")
            return redirect('story-upload')

        # Check if it's an image or a video
        is_video = media.name.endswith(('mp4', 'mov', 'avi'))
        is_image = media.name.endswith(('jpg', 'jpeg', 'png', 'gif'))

        if not (is_video or is_image):  # Make sure it's either an image or a video
            messages.error(request, "Only image or video files are allowed.")
            return redirect('story-upload')

        if is_video and media.size > 10 * 1024 * 1024:  # Optional: 10MB limit for videos
            messages.error(request, "Video is too large.")
            return redirect('story-upload')

        # Upload media to Cloudinary
        try:
            if is_video:
                cloudinary_response = upload(media, resource_type='video')  # Specify resource_type='video' for videos
            elif is_image:
                cloudinary_response = upload(media, resource_type='image')  # Specify resource_type='image' for images

            media_url = cloudinary_response['secure_url']
        except Exception as e:
            messages.error(request, f"Error uploading media: {str(e)}")
            return redirect('story-upload')

        # Create the Story object with the Cloudinary URL
        story = Story.objects.create(
            user=request.user,
            media=media_url,
            caption=caption,
            is_video=is_video
        )

        return redirect('story-detail', story_id=story.id)

    return render(request, 'posts/story_upload.html')

@login_required
def share_story(request, story_id):
    if request.method == 'POST':
        shared_with_username = request.POST.get('shared_with_username')
        story = get_object_or_404(Story, id=story_id)

        try:
            user_to_share = CustomUser.objects.get(username=shared_with_username)
            Notification.objects.create(
                user=user_to_share,
                message=f"{request.user.username} shared a <a href='{reverse('story-detail', args=[story.id])}'>story</a> with you!"
            )
            story.shared_by = request.user
            story.save()
            messages.success(request, "Story shared successfully!")
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found.")

    return redirect('story-detail', story_id=story_id)
@login_required
def view_story(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    print(f"Story created at: {story.created_at}, Expiry status: {story.is_expired()}")
    
    if story.is_expired():
        messages.error(request, "This story has expired.")
        return redirect('post-list')

    if request.user not in story.viewers.all():
        story.viewers.add(request.user)
        print(f"User {request.user.username} added to viewers.")

    return render(request, 'posts/story_detail.html', {'story': story})

@login_required
def delete_story(request, story_id):
    story = get_object_or_404(Story, id=story_id, user=request.user)

    if request.method == "POST":
        # Get the next story before deleting
        next_story = Story.objects.filter(
            created_at__gt=story.created_at
        ).order_by('created_at').first()

        story.delete()

        if next_story:
            return redirect('story-detail', next_story.id)
        else:
            return redirect('story-detail')  # fallback if no next story

    return redirect('story-detail', story_id)
@login_required
def story_detail_view(request, story_id=None):
    # If no story_id is given, get the latest story from the current user
    if story_id is None:
        try:
            story = Story.objects.filter(user=request.user).latest('created_at')
        except Story.DoesNotExist:
            return redirect('story-upload')
    else:
        story = get_object_or_404(Story, id=story_id)

    # Get all other users' stories, excluding the current user's
    all_stories = Story.objects.exclude(user=request.user).order_by('-created_at')

    # Get the index of the current story
    current_index = list(all_stories).index(story) if story in all_stories else None

    # Ensure previous_story and next_story are assigned only if the index is valid
    previous_story = all_stories[current_index - 1] if current_index and current_index > 0 else None
    next_story = all_stories[current_index + 1] if current_index and current_index < len(all_stories) - 1 else None

    return render(request, 'posts/story_detail.html', {
        'story': story,
        'previous_story': previous_story,
        'next_story': next_story,
        'all_stories': all_stories,  # Pass all other stories
    })

def story_list_view(request):
    # Fetch all stories ordered by creation date or as needed
    stories = Story.objects.all().order_by('-created_at')  # Adjust your query as needed
    
    # Pagination logic
    paginator = Paginator(stories, 10)  # Show 10 stories per page (you can adjust this)
    page_number = request.GET.get('page')  # Get the page number from the URL
    page_obj = paginator.get_page(page_number)  # Get the corresponding page object
    
    # Pass the page_obj to the template
    return render(request, 'posts/story_list.html', {'page_obj': page_obj})
@login_required
def my_story_view(request):
    latest_story = Story.objects.filter(user=request.user).order_by('-created_at').first()
    if latest_story:
        return redirect('story-detail', story_id=latest_story.id)
    else:
        return redirect('story-upload')
def like_story(request, story_id):
    if request.method == 'POST':
        story = get_object_or_404(Story, id=story_id)
        if request.user in story.likes.all():
            story.likes.remove(request.user)
        else:
            story.likes.add(request.user)

            # Create a notification (only if new Like)
            if story.user != request.user:
                Notification.objects.create(
                    user=story.user,
                    sender=request.user,
                    notification_type='like_story',
                    story=story
                )
        
        # Return the updated like count and a boolean for like/unlike state
        return JsonResponse({
            'like_count': story.likes.count(),
            'is_liked': request.user in story.likes.all()
        })
    return JsonResponse({'error': 'Bad Request'}, status=400)
def send_story_message(request, username):
    if request.method == 'POST':
        receiver = get_object_or_404(User, username=username)
        message_text = request.POST.get('message')
        Message.objects.create(sender=request.user, receiver=receiver, content=message_text)
        return redirect('inbox')
from django.db.models import Q
from django.views.decorators.http import require_GET
@require_GET
def mention_suggestions(request):
    query = request.GET.get('q', '')
    users = User.objects.filter(username__icontains=query)[:5]
    usernames = list(users.values_list('username', flat=True))
    return JsonResponse(usernames, safe=False)
def reel_list(request):
    reels = Reel.objects.all()  # Fetch all the reels
    for reel in reels:
        reel.is_liked = reel.is_liked_by(request.user)
        reel.is_saved = reel.is_saved_by(request.user)
    return render(request, 'posts/reel_list.html', {'reels': reels})
@login_required
def like_reel(request, reel_id):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            reel = Reel.objects.get(id=reel_id)
            user = request.user
            liked = False

            if user in reel.likes.all():
                reel.likes.remove(user)
                liked = False
            else:
                reel.likes.add(user)
                liked = True

                # ✅ Send notification if user is not the reel owner
                if reel.user != user:
                    Notification.objects.create(
                        user=reel.user,  # recipient
                        sender=user,     # actor
                        notification_type='reel_like',
                        message=f"{user.username} liked your reel.",
                        link=f"/reels/{reel.id}/"  # adjust URL if different
                    )

            return JsonResponse({'liked': liked, 'total_likes': reel.likes.count()})
        except Reel.DoesNotExist:
            return JsonResponse({'error': 'Reel not found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
@require_POST
def share_reel(request):
    reel_id = request.POST.get('reel_id')
    user_ids = request.POST.getlist('user_ids[]')  # JS sends array

    reel = get_object_or_404(Reel, id=reel_id)

    # Example: Assuming Reel model has a ManyToMany field `shared_with` for users
    users_to_share = User.objects.filter(id__in=user_ids)

    # Add those users to the reel's shared_with field
    for user in users_to_share:
        reel.shared_with.add(user)

    reel.save()

    return JsonResponse({'success': True, 'message': 'Reel shared successfully.'})
def reel_comments(request, reel_id):
    reel = get_object_or_404(Reel, id=reel_id)
    content_type = ContentType.objects.get_for_model(reel)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.content_type = content_type
            comment.object_id = reel.id
            comment.save()
            return redirect('reel_comments', reel_id=reel.id)
    else:
        form = CommentForm()

    # ✅ Fetch all comments for this reel manually
    comments = Comment.objects.filter(content_type=content_type, object_id=reel.id,parent__isnull=True ).order_by('-created_at')

    return render(request, 'posts/reel_comments.html', {
        'form': form,
        'reel': reel,
        'comments': comments
    })
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    related_obj = comment.content_object  # could be Reel or Post

    print(f"Deleting comment {comment_id} from object {related_obj}")
    print(f"Comment Owner: {comment.user}, Object Owner: {related_obj.user}, Logged-in User: {request.user}")

    if request.user == comment.user or request.user == related_obj.user:
        comment.delete()
        print("Comment deleted successfully.")
    else:
        print("User not authorized to delete this comment.")

    # Redirect depending on object type (post or reel)
    if hasattr(related_obj, 'title'):  # example check: Post may have title
        return redirect('post-list')
    else:
        return redirect('reel_comments', reel_id=related_obj.id)
@login_required
def like_comment(request, comment_id):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        comment = get_object_or_404(Comment, id=comment_id)
        user = request.user
        liked = False

        if user in comment.likes.all():
            comment.likes.remove(user)
        else:
            comment.likes.add(user)
            liked = True

            # ✅ Notification
            if comment.user != user:
                Notification.objects.create(
                    user=comment.user,
                    sender=user,
                    notification_type='comment_like',
                    message=f"{user.username} liked your comment.",
                    link=f"/posts/{comment.post.id}/",
                    image=user.profile.profile_pic.url if user.profile.profile_pic else ""
                )

        return JsonResponse({
            'liked': liked,
            'total_likes': comment.likes.count()
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)
@login_required
@csrf_exempt
def reply_to_comment(request, comment_id):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = json.loads(request.body)
        reply_text = data.get('reply')

        parent_comment = get_object_or_404(Comment, id=comment_id)

        # Get content_object from parent
        content_type = parent_comment.content_type
        object_id = parent_comment.object_id

        # Create reply (linked to parent and same object)
        reply = Comment.objects.create(
            parent=parent_comment,  
            user=request.user,
            content=reply_text,
            content_type=content_type,
            object_id=object_id
        )
        

        # Send notification
        if parent_comment.user != request.user:
            Notification.objects.create(
                user=parent_comment.user,
                sender=request.user,
                notification_type='comment_reply',
                message=f"{request.user.username} replied to your comment.",
                link=f"/posts/{object_id}/",
                image=request.user.profile.profile_pic.url if hasattr(request.user, 'profile') and request.user.profile.profile_pic else ""
            )

        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def save_reel(request, reel_id):
    if request.method == 'POST':
        try:
            reel = Reel.objects.get(id=reel_id)
            if request.user in reel.saved_by.all():
                reel.saved_by.remove(request.user)
                saved = False
            else:
                reel.saved_by.add(request.user)
                saved = True
            return JsonResponse({'saved': saved})
        except Reel.DoesNotExist:
            return JsonResponse({'error': 'Reel not found'}, status=404)
    return JsonResponse({'error': 'Invalid method'}, status=400)
from .models import Reel, Report 
@login_required
def report_reel(request, reel_id):
    if request.method == 'POST':
        reason = request.POST.get('reason')
        reel = get_object_or_404(Reel, id=reel_id)
        report = Report.objects.create(user=request.user, reel=reel, reason=reason)
        return JsonResponse({'success': True, 'message': 'Report submitted successfully.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)

from django.contrib.admin.views.decorators import staff_member_required
@staff_member_required
def view_reports(request):
    reports = Report.objects.select_related('user', 'reel').order_by('-created_at')
    return render(request, 'posts/view_reports.html', {'reports': reports})

@csrf_exempt
def unsave_post(request):
    if request.method == 'POST' and request.user.is_authenticated:
        post_id = request.POST.get('post_id')
        try:
            post = Post.objects.get(id=post_id)
            post.saved_by.remove(request.user)
            return JsonResponse({'status': 'unsaved'})
        except Post.DoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=404)
    return JsonResponse({'error': 'Invalid request'}, status=400)
@login_required
def saved_content(request):
    user = request.user
    saved_posts = Post.objects.filter(saved_by=user)

    # Separate image posts and video reels
    image_posts = saved_posts.filter(video='').distinct()
    video_reels = saved_posts.exclude(video='').distinct()

    return render(request, 'posts/saved.html', {
        'image_posts': image_posts,
        'video_reels': video_reels
    })
@login_required
def saved_posts_view(request):
    saved_posts = Post.objects.filter(saved_by=request.user, video__isnull=True)
    return render(request, 'posts/saved_posts.html', {'saved_posts': saved_posts})
@login_required
def saved_reels_view(request):
    saved_reels = Post.objects.filter(saved_by=request.user, video__isnull=False)
    return render(request, 'posts/saved_reels.html', {'saved_reels': saved_reels})