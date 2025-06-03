from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Photo, Tag, PhotoLike, PhotoDislike
from .forms import PhotoSearchForm

def home(request):
    # Get featured photos (latest 6 photos)
    featured_photos = Photo.objects.select_related('uploaded_by').prefetch_related('tags')[:6]
    
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
    return render(request, 'home.html', context)

def photo_list(request):
    form = PhotoSearchForm(request.GET)
    photos = Photo.objects.select_related('uploaded_by').prefetch_related('tags')
    
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
    paginator = Paginator(photos, 12)  # Show 12 photos per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'photos': page_obj,
    }
    return render(request, 'photo_list.html', context)

def photo_detail(request, photo_id):
    photo = get_object_or_404(
        Photo.objects.select_related('uploaded_by').prefetch_related('tags'),
        id=photo_id
    )
    
    # Check if user has liked or disliked the photo
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
    return render(request, 'photo_detail.html', context)

def photos_by_tag(request, tag):
    tag_obj = get_object_or_404(Tag, name=tag)
    photos = Photo.objects.filter(tags=tag_obj).select_related('uploaded_by').prefetch_related('tags')
    
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
    
    if request.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'likes_count': photo.get_likes_count(),
            'dislikes_count': photo.get_dislikes_count(),
        })
    
    return redirect('gallery:photo_detail', photo_id=photo.id)

@login_required
def dislike_photo(request, photo_id):
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
    
    if request.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse({
            'disliked': disliked,
            'likes_count': photo.get_likes_count(),
            'dislikes_count': photo.get_dislikes_count(),
        })
    
    return redirect('gallery:photo_detail', photo_id=photo.id)