from django.urls import path, include
from . import views
from .views import delete_post
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.PostList.as_view(), name='home'),
    path('profile/', views.profile, name='profile'),
    path('about/', views.about, name='about'),
    path('gallery/', views.gallery, name='gallery'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('addpost/', views.AddPostView.as_view(), name='add_post'),
    path('post/edit/<int:pk>/', views.UpdatePost.as_view(),
         name='update_post'),
    path('postdetail/<int:pk>/', views.PostDetail.as_view(),
         name='post_detail'),
    path('post/<int:post_id>/delete/', delete_post, name='delete_post'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
