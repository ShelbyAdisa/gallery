# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from django.contrib.auth.models import User
# # from gallery.models import Tag, Photo, PhotoLike, PhotoDislike

# class CustomUserAdmin(UserAdmin):
#     list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
#     list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')

# # Unregister the default User admin and register our custom one
# admin.site.unregister(User)
# admin.site.register(User, CustomUserAdmin)

# @admin.register(Tag)
# class TagAdmin(admin.ModelAdmin):
#     list_display = ('name', 'created_at')
#     list_filter = ('created_at',)
#     search_fields = ('name',)
#     readonly_fields = ('created_at',)

# @admin.register(Photo)
# class PhotoAdmin(admin.ModelAdmin):
#     list_display = ('title', 'uploaded_by', 'created_at', 'get_likes_count', 'get_dislikes_count')
#     list_filter = ('created_at', 'updated_at', 'uploaded_by')
#     search_fields = ('title', 'description', 'uploaded_by__username')
#     readonly_fields = ('created_at', 'updated_at', 'get_likes_count', 'get_dislikes_count')
#     filter_horizontal = ('tags',)
    
#     def get_likes_count(self, obj):
#         return obj.get_likes_count()
#     get_likes_count.short_description = 'Likes'
    
#     def get_dislikes_count(self, obj):
#         return obj.get_dislikes_count()
#     get_dislikes_count.short_description = 'Dislikes'

# @admin.register(PhotoLike)
# class PhotoLikeAdmin(admin.ModelAdmin):
#     list_display = ('user', 'photo', 'created_at')
#     list_filter = ('created_at',)
#     search_fields = ('user__username', 'photo__title')
#     readonly_fields = ('created_at',)

# @admin.register(PhotoDislike)
# class PhotoDislikeAdmin(admin.ModelAdmin):
#     list_display = ('user', 'photo', 'created_at')
#     list_filter = ('created_at',)
#     search_fields = ('user__username', 'photo__title')
#     readonly_fields = ('created_at',)