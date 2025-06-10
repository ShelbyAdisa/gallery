from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    # path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('upload/', views.upload_photo, name='upload_photo'),
    path('delete_photo/<int:photo_id>/', views.delete_photo, name='delete_photo'),
]
