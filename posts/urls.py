from django.urls import path
from .views import (
    PostListView, PostCreateView, PostDetailView, 
    PostUpdateView, PostDeleteView, like_post, save_post, add_comment
)

urlpatterns = [
    path('', PostListView.as_view(), name='post-list'),
    path('create/', PostCreateView.as_view(), name='post-create'),
    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('<int:post_id>/like/', like_post, name='like-post'),
    path('<int:post_id>/save/', save_post, name='save-post'),
    path('<int:post_id>/comment/', add_comment, name='add-comment'),
]
