from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages

def home(request):
    """
    Home page view - redirects to gallery home
    """
    return redirect('gallery:home')

def about(request):
    """
    About page view
    """
    context = {
        'title': 'About Photo Gallery',
        'description': 'Learn more about our photo gallery platform',
    }
    return render(request, 'core/about.html', context)

def contact(request):
    """
    Contact page view
    """
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Here you would typically send an email or save to database
        # For now, we'll just show a success message
        messages.success(request, 'Thank you for your message! We will get back to you soon.')
        return redirect('core:contact')
    
    context = {
        'title': 'Contact Us',
    }
    return render(request, 'core/contact.html', context)

def privacy_policy(request):
    """
    Privacy policy page view
    """
    context = {
        'title': 'Privacy Policy',
    }
    return render(request, 'core/privacy.html', context)

def terms_of_service(request):
    """
    Terms of service page view
    """
    context = {
        'title': 'Terms of Service',
    }
    return render(request, 'core/terms.html', context)