from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Tag, Photo, PhotoLike, PhotoDislike

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')

# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# @admin.register(Tag)
# class TagAdmin(admin.ModelAdmin):
#     list_display = ('name', 'created_at')
#     list_filter = ('created_at',)
#     search_fields = ('name',)
#     readonly_fields = ('created_at',)

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at')  # Use the actual field name
    list_filter = ('uploaded_at', 'tags')  # Use actual fields
    search_fields = ('title', 'description')
    readonly_fields = ('uploaded_at',)
    filter_horizontal = ('tags',)  # This works since you have ManyToManyField
    
    # Remove these methods if your model doesn't have like/dislike functionality yet
    # def get_likes_count(self, obj):
    #     return obj.get_likes_count()
    # get_likes_count.short_description = 'Likes'
    # 
    # def get_dislikes_count(self, obj):
    #     return obj.get_dislikes_count()
    # get_dislikes_count.short_description = 'Dislikes'

# Only register these if the models exist and have the required fields
@admin.register(PhotoLike)
class PhotoLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'photo') 
    search_fields = ('user__username', 'photo__title')

@admin.register(PhotoDislike)
class PhotoDislikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'photo') 
    search_fields = ('user__username', 'photo__title')