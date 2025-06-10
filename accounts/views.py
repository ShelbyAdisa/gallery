from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Photo
from django.contrib.auth import logout
from .forms import PhotoUploadForm

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # Log user in after registration
            messages.success(request, "Registration successful!")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            
            # Handle remember me functionality
            if not remember_me:
                request.session.set_expiry(0)  # Session expires when browser closes
            
            # Redirect to profile page
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')


@login_required
def profile_view(request):
    # Get user's photos with pagination
    user_photos = Photo.objects.filter(user=request.user).order_by('-uploaded_at')
    paginator = Paginator(user_photos, 12)  # Show 12 photos per page
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'user': request.user,
        'photos': page_obj,
        'total_photos': user_photos.count(),
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def upload_photo(request):
    if request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        photo_file = request.FILES.get('photo')
        
        if photo_file:
            # Create new photo instance
            photo = Photo.objects.create(
                user=request.user,
                title=title,
                description=description,
                image=photo_file
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # AJAX request - return JSON response
                return JsonResponse({
                    'success': True,
                    'message': 'Photo uploaded successfully!',
                    'photo_id': photo.id,
                    'photo_url': photo.image.url
                })
            else:
                messages.success(request, 'Photo uploaded successfully!')
                return redirect('accounts:profile')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Please select a photo to upload.'
                })
            else:
                messages.error(request, 'Please select a photo to upload.')
    
    return redirect('accounts:profile')


@login_required
def delete_photo(request, photo_id):
    try:
        photo = Photo.objects.get(id=photo_id, user=request.user)
        photo.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Photo deleted successfully!'})
        else:
            messages.success(request, 'Photo deleted successfully!')
    except Photo.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Photo not found.'})
        else:
            messages.error(request, 'Photo not found.')
    
    return redirect('accounts:profile')
def logout_view(request):
    logout(request)
    messages.success(request, "You’ve been logged out.")
    return redirect('accounts:login')

def home(request):
    """Display all photos in the gallery"""
    photos = Photo.objects.all()[:12]  # Show latest 12 photos
    return render(request, 'gallery/home.html', {
        'photos': photos
    })

@login_required
def upload_photo(request):
    """Handle photo upload"""
    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.uploaded_by = request.user
            photo.save()
            messages.success(request, 'Your photo has been uploaded successfully!')
            return redirect('gallery:home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PhotoUploadForm()
    
    return render(request, 'gallery/upload.html', {
        'form': form
    })