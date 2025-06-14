from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
    path('', views.home, name='home'),
    path('photo/<int:photo_id>/', views.photo_detail, name='photo_detail'),
    path('photos/', views.photo_list, name='photo_list'),
    path('photos/tag/<str:tag>/', views.photos_by_tag, name='photos_by_tag'),
    path('photo/<int:photo_id>/like/', views.like_photo, name='like_photo'),
    path('photo/<int:photo_id>/dislike/', views.dislike_photo, name='dislike_photo'),
    path('upload/', views.upload_photo, name='upload_photo'),
    path('delete_photo/<int:photo_id>/', views.delete_photo, name='delete_photo'),
    path('my-photos/', views.my_photos, name='my_photos'),

]
