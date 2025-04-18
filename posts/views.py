from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Post, Comment,Message
from users.models import CustomUser
from posts.forms import MessageForm
from django.utils.timezone import localtime
import json
from django.http import JsonResponse # Ensure Post model is imported
from django.contrib.auth import get_user_model

class PostListView(ListView):
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    ordering = ['-created_at']
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['content', 'image', 'video']
    template_name = 'posts/post_form.html'
    success_url = reverse_lazy('post-list')

    def form_valid(self, form):
        image = form.cleaned_data.get('image')
        video = form.cleaned_data.get('video')

        if image and video:
            form.add_error('video', "You can't upload both an image and a video in the same post.")
            return self.form_invalid(form)

        form.instance.user = self.request.user
        return super().form_valid(form)


class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = Comment.objects.filter(post=self.object)
        
        print("Comments for Post:", self.object.id)
        for comment in comments:
            print(f"User: {comment.user}, Content: {comment.content}")

        context['comments'] = comments
        return context

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['content', 'image','video']
    template_name = 'posts/post_form.html'
    success_url = reverse_lazy('post-list')

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)

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
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            comment = Comment.objects.create(user=request.user, post=post, content=content)
            print(f"New Comment Added by {comment.user}: {comment.content}")

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
            return redirect('inbox')
    else:
        form = MessageForm()
    return render(request, 'posts/send_message.html', {'form': form, 'receiver': receiver})

@login_required
def inbox(request):
    received_messages = Message.objects.filter(receiver=request.user).order_by('-timestamp')
    return render(request, 'posts/inbox.html', {'messages': received_messages})

@login_required
def chat_room(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    current_user = request.user

    # Generate consistent room name (e.g., "1_2" or "2_1")
    room_name = f"{min(current_user.id, other_user.id)}_{max(current_user.id, other_user.id)}"
    
    return render(request, 'posts/chat_room.html', {
        'room_name': room_name,
        'other_user': other_user,
    })