"""Utilities for sending booking-related emails."""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def send_booking_cancellation_email(booking):
    """
    Send a booking cancellation confirmation email to the user.
    
    Args:
        booking: The Booking object being cancelled
    """
    if not booking.user or not booking.user.email:
        return False
    
    try:
        subject = f"Booking Cancellation Confirmation - {booking.restaurant.name}"
        
        context = {
            'user_name': booking.user.first_name or booking.user.username,
            'restaurant_name': booking.restaurant.name,
            'booking_date': booking.date.strftime('%d %B %Y at %H:%M'),
            'guests': booking.guests,
            'special_requests': booking.special_requests or 'None',
        }
        
        # Try to use HTML template; fall back to plain text
        try:
            html_message = render_to_string('bookings/email/cancellation_confirmation.html', context)
        except:
            html_message = None
        
        # Plain text version
        text_message = render_to_string('bookings/email/cancellation_confirmation.txt', context)
        
        send_mail(
            subject,
            text_message,
            settings.DEFAULT_FROM_EMAIL,
            [booking.user.email],
            html_message=html_message,
            fail_silently=True,  # Don't crash if email fails
        )
        return True
    except Exception as e:
        # Log the error but don't prevent booking cancellation
        print(f"Error sending cancellation email for booking {booking.pk}: {e}")
        import traceback
        traceback.print_exc()
        return False
