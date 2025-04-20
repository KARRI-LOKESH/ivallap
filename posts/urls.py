from django.urls import path
from .views import (
    PostListView, PostCreateView, PostDetailView, 
    PostUpdateView, PostDeleteView, like_post, 
    save_post, add_comment, delete_comment, 
    dashboard, send_message, inbox, chat_room,share_post,notifications_view
)

urlpatterns = [
    path('', PostListView.as_view(), name='post-list'),
    path('create/', PostCreateView.as_view(), name='post-create'),
    path('<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('like/<int:post_id>/', like_post, name="like-post"),
    path('save/<int:post_id>/', save_post, name="save-post"),
    path('comments/<int:comment_id>/delete/', delete_comment, name="comment-delete"),
    path('posts/<int:post_id>/comment/', add_comment, name="add-comment"),
    path('dashboard/', dashboard, name='dashboard'),
    path('send/<int:receiver_id>/', send_message, name='send-message'),
    path('inbox/', inbox, name='inbox'),
    path('share/<int:post_id>/', share_post, name='share-post'),
    path('posts/posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('chat/<int:user_id>/', chat_room, name='chat-room'),
    path('notifications/', notifications_view, name='notifications'),

]
