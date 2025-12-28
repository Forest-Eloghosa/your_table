from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ProfilePictureForm
from .models import Profile

# Create your views here.

@login_required
def profile_view(request):
    """User profile showing all booking history and changes."""
    from bookings.models import Booking, BookingHistory
    
    # Ensure user has a profile (for existing users who don't have one yet)
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    # Handle profile picture upload
    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile picture updated successfully!')
            return redirect('users:profile')
    else:
        form = ProfilePictureForm(instance=profile)
    
    # Get all bookings (including soft-deleted) for the user
    try:
        base_manager = getattr(Booking, 'all_objects', Booking.objects)
        bookings = base_manager.filter(user=request.user).order_by('-created_at')
    except Exception:
        bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    
    # Get all booking history for the user
    history = BookingHistory.objects.filter(user=request.user).order_by('-timestamp')[:50]
    
    context = {
        'bookings': bookings,
        'booking_history': history,
        'profile_form': form,
    }
    return render(request, 'registration/profile.html', context)


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created. You can now log in.')
            return redirect('account_login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
 