from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict
import traceback


def _safe_get_model(app_label, model_name):
    try:
        from django.apps import apps

        return apps.get_model(app_label, model_name)
    except Exception:
        return None


@receiver(post_save)
def booking_saved(sender, instance, created, **kwargs):
    # Only handle Booking saves
    Booking = _safe_get_model('bookings', 'Booking')
    if Booking is None or sender != Booking:
        return

    BookingHistory = _safe_get_model('bookings', 'BookingHistory')
    # snapshot relevant fields
    try:
        data = model_to_dict(instance, fields=['id', 'user', 'restaurant', 'date', 'guests', 'special_requests', 'created_at'])
        data['user'] = data.get('user') and int(data['user'])
        data['restaurant'] = data.get('restaurant') and int(data['restaurant'])
        if data.get('date'):
            try:
                data['date'] = instance.date.isoformat()
            except Exception:
                pass
        action = 'created' if created else 'updated'
        if BookingHistory is not None:
            try:
                BookingHistory.objects.create(
                    booking=instance if created else instance,
                    booking_pk=instance.pk,
                    user=instance.user if hasattr(instance, 'user') else None,
                    action=action,
                    data=data,
                )
            except Exception:
                # don't let history failures break the main save; log to stderr
                traceback.print_exc()
    except Exception:
        traceback.print_exc()


@receiver(post_delete)
def booking_deleted(sender, instance, **kwargs):
    Booking = _safe_get_model('bookings', 'Booking')
    if Booking is None or sender != Booking:
        return

    BookingHistory = _safe_get_model('bookings', 'BookingHistory')
    try:
        data = model_to_dict(instance, fields=['id', 'user', 'restaurant', 'date', 'guests', 'special_requests', 'created_at'])
        data['user'] = data.get('user') and int(data['user'])
        data['restaurant'] = data.get('restaurant') and int(data['restaurant'])
        if data.get('date'):
            try:
                data['date'] = instance.date.isoformat()
            except Exception:
                pass
        if BookingHistory is not None:
            try:
                BookingHistory.objects.create(
                    booking=None,
                    booking_pk=instance.pk,
                    user=instance.user if hasattr(instance, 'user') else None,
                    action='deleted',
                    data=data,
                )
            except Exception:
                traceback.print_exc()
    except Exception:
        traceback.print_exc()
