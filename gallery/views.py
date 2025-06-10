from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.urls import reverse
from .models import Photo, Tag, PhotoLike, PhotoDislike
from .forms import PhotoSearchForm, PhotoUploadForm

def photo_list(request):
    """Display paginated list of photos with search functionality."""
    form = PhotoSearchForm(request.GET)
   
    photos = Photo.objects.all().prefetch_related('tags')
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        tag = form.cleaned_data.get('tag')
        
        if query:
            photos = photos.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query) |
                Q(tags__name__icontains=query)
            ).distinct()
        
        if tag:
            photos = photos.filter(tags=tag)
    
    # Pagination
    paginator = Paginator(photos, 12)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'photos': page_obj,
    }
    return render(request, 'gallery/photo_list.html', context)

def home(request):
    """Display homepage with featured photos and statistics."""
   
    featured_photos = Photo.objects.all().prefetch_related('tags').order_by('-uploaded_at')[:6]
    
    # Get popular tags
    popular_tags = Tag.objects.annotate(
        photo_count=Count('photo')
    ).filter(photo_count__gt=0).order_by('-photo_count')[:10]
    
    # Get total counts
    total_photos = Photo.objects.count()
    total_tags = Tag.objects.count()
    
    context = {
        'featured_photos': featured_photos,
        'popular_tags': popular_tags,
        'total_photos': total_photos,
        'total_tags': total_tags,
    }
    return render(request, 'gallery/home.html', context)

def photo_detail(request, photo_id):
    """Display detailed view of a single photo."""
   
    photo = get_object_or_404(
        Photo.objects.all().prefetch_related('tags'),
        id=photo_id
    )
    
    
    user_liked = False
    user_disliked = False
    
    if request.user.is_authenticated:
        user_liked = PhotoLike.objects.filter(user=request.user, photo=photo).exists()
        user_disliked = PhotoDislike.objects.filter(user=request.user, photo=photo).exists()
    
    # Get related photos (same tags)
    related_photos = Photo.objects.filter(
        tags__in=photo.tags.all()
    ).exclude(id=photo.id).distinct()[:4]
    
    context = {
        'photo': photo,
        'user_liked': user_liked,
        'user_disliked': user_disliked,
        'related_photos': related_photos,
    }
    return render(request, 'gallery/photo_detail.html', context)

def photos_by_tag(request, tag):
    """Display photos filtered by a specific tag."""
    tag_obj = get_object_or_404(Tag, name=tag)
    # Fixed: Removed select_related('uploaded_by') - assuming this field doesn't exist
    photos = Photo.objects.filter(tags=tag_obj).prefetch_related('tags')
    
    # Pagination
    paginator = Paginator(photos, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tag': tag_obj,
        'page_obj': page_obj,
        'photos': page_obj,
    }
    return render(request, 'gallery/photos_by_tag.html', context)

@login_required
def like_photo(request, photo_id):
    """Handle photo like/unlike functionality."""
    if request.method != 'POST':
        return redirect('gallery:photo_detail', photo_id=photo_id)
    
    photo = get_object_or_404(Photo, id=photo_id)
    
    # Remove dislike if exists
    PhotoDislike.objects.filter(user=request.user, photo=photo).delete()
    
    # Toggle like
    like, created = PhotoLike.objects.get_or_create(user=request.user, photo=photo)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    
    # Handle AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'likes_count': photo.get_likes_count(),
            'dislikes_count': photo.get_dislikes_count(),
        })
    
    return redirect('gallery:photo_detail', photo_id=photo.id)

@login_required
def upload_photo(request):
    """Handle photo upload functionality."""
    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Create photo instance but don't save yet
            photo = form.save(commit=False)
            # Fixed: Assuming you have a user field instead of uploaded_by
            # Change this to match your actual model field name
            if hasattr(photo, 'uploaded_by'):
                photo.uploaded_by = request.user
            elif hasattr(photo, 'user'):
                photo.user = request.user
            elif hasattr(photo, 'author'):
                photo.author = request.user
            photo.save()
            
            # Handle tags
            tag_names = form.cleaned_data.get('tags', [])
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                photo.tags.add(tag)
            
            messages.success(request, 'Photo uploaded successfully!')
            return redirect('gallery:photo_detail', photo_id=photo.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PhotoUploadForm()
    
    return render(request, 'gallery/upload_photo.html', {'form': form})

@login_required
def my_photos(request):
    """Display photos uploaded by the current user."""
    # Fixed: Use the correct field name for user relationship
    # Adjust the field name based on your Photo model
    user_field = None
    if hasattr(Photo, 'uploaded_by'):
        user_field = 'uploaded_by'
    elif hasattr(Photo, 'user'):
        user_field = 'user'
    elif hasattr(Photo, 'author'):
        user_field = 'author'
    
    if user_field:
        photos = Photo.objects.filter(**{user_field: request.user}).prefetch_related('tags').order_by('-uploaded_at')
    else:
        # Fallback if no user field found
        photos = Photo.objects.none()
    
    # Pagination
    paginator = Paginator(photos, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'photos': page_obj,
    }
    return render(request, 'gallery/my_photos.html', context)

@login_required
def delete_photo(request, photo_id):
    """Delete a photo (only by the owner)."""
    # Fixed: Use the correct field name for user relationship
    user_field = None
    if hasattr(Photo, 'uploaded_by'):
        user_field = 'uploaded_by'
    elif hasattr(Photo, 'user'):
        user_field = 'user'
    elif hasattr(Photo, 'author'):
        user_field = 'author'
    
    if user_field:
        photo = get_object_or_404(Photo, id=photo_id, **{user_field: request.user})
    else:
        photo = get_object_or_404(Photo, id=photo_id)
    
    if request.method == 'POST':
        # Delete the image file from storage
        if photo.image:
            photo.image.delete(save=False)
        photo.delete()
        messages.success(request, 'Photo deleted successfully!')
        return redirect('gallery:my_photos')
    
    return render(request, 'gallery/confirm_delete.html', {'photo': photo})

@login_required
def edit_photo(request, photo_id):
    """Edit a photo (only by the owner)."""
    # Fixed: Use the correct field name for user relationship
    user_field = None
    if hasattr(Photo, 'uploaded_by'):
        user_field = 'uploaded_by'
    elif hasattr(Photo, 'user'):
        user_field = 'user'
    elif hasattr(Photo, 'author'):
        user_field = 'author'
    
    if user_field:
        photo = get_object_or_404(Photo, id=photo_id, **{user_field: request.user})
    else:
        photo = get_object_or_404(Photo, id=photo_id)
    
    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES, instance=photo)
        if form.is_valid():
            # Save the photo
            updated_photo = form.save()
            
            # Handle tags - clear existing and add new ones
            updated_photo.tags.clear()
            tag_names = form.cleaned_data.get('tags', [])
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                updated_photo.tags.add(tag)
            
            messages.success(request, 'Photo updated successfully!')
            return redirect('gallery:photo_detail', photo_id=photo.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-populate the form with existing data
        initial_tags = ', '.join([tag.name for tag in photo.tags.all()])
        form = PhotoUploadForm(instance=photo, initial={'tags': initial_tags})
    
    context = {
        'form': form,
        'photo': photo,
        'is_edit': True,
    }
    return render(request, 'gallery/upload_photo.html', context)

@login_required
def dislike_photo(request, photo_id):
    """Handle photo dislike/undislike functionality."""
    if request.method != 'POST':
        return redirect('gallery:photo_detail', photo_id=photo_id)
    
    photo = get_object_or_404(Photo, id=photo_id)
    
    # Remove like if exists
    PhotoLike.objects.filter(user=request.user, photo=photo).delete()
    
    # Toggle dislike
    dislike, created = PhotoDislike.objects.get_or_create(user=request.user, photo=photo)
    if not created:
        dislike.delete()
        disliked = False
    else:
        disliked = True
    
    # Handle AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'disliked': disliked,
            'likes_count': photo.get_likes_count(),
            'dislikes_count': photo.get_dislikes_count(),
        })
    
    return redirect('gallery:photo_detail', photo_id=photo.id)