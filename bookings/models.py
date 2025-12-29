from django.db import models
from django.utils import timezone
from django.forms.models import model_to_dict
from django.apps import apps
from cloudinary.models import CloudinaryField

# Create your models here.

class BookingQuerySet(models.QuerySet):
    """
    Custom QuerySet to handle soft-deleted bookings.
    Overrides delete() to perform soft-delete.
    """
    def delete(self):
        # Soft-delete: mark as deleted and set deleted_at
        return self.update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()


class BookingManager(models.Manager):
    def get_queryset(self):
        return BookingQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def all_objects(self):
        return BookingQuerySet(self.model, using=self._db)

 
class Booking(models.Model):
    """
    user is a ForeignKey to the User model.
    Soft-deletion is implemented via `is_deleted` and `deleted_at` fields.
    restaurant is a ForeignKey to the Restaurant model in the menu app.
    guests is a PositiveIntegerField representing number of guests.
    special_requests is an optional TextField for any special requests.
    created_at is a DateTimeField automatically set on creation.
    """
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    restaurant = models.ForeignKey('menu.Restaurant', on_delete=models.CASCADE)
    date = models.DateTimeField()
    guests = models.PositiveIntegerField()
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # managers
    objects = BookingManager()
    all_objects = BookingManager()

    def clean(self):
        # Prevent bookings in the past
        if self.date and self.date < timezone.now():
            from django.core.exceptions import ValidationError

            raise ValidationError({'date': 'Booking date/time cannot be in the past.'})

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking for {self.guests} at {self.restaurant} on {self.date}"

    def delete(self, using=None, keep_parents=False):
        """
        Soft-delete the booking and record a BookingHistory 'deleted' event.

        This avoids removing the DB row so users/admins can still see historical
        bookings. If history creation fails we log but still mark the booking as deleted.
        """
        try:
            BookingHistory = apps.get_model('bookings', 'BookingHistory')
            # snapshot relevant fields
            data = model_to_dict(self, fields=['id', 'user', 'restaurant', 'date', 'guests', 'special_requests', 'created_at'])
            data['user'] = data.get('user') and int(data['user'])
            data['restaurant'] = data.get('restaurant') and int(data['restaurant'])
            if data.get('date') and hasattr(self, 'date'):
                try:
                    data['date'] = self.date.isoformat()
                except Exception:
                    pass
            # mark soft-delete
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save(update_fields=['is_deleted', 'deleted_at'])
            # create history record
            if BookingHistory is not None:
                try:
                    BookingHistory.objects.create(
                        booking=None,
                        booking_pk=self.pk,
                        user=self.user if hasattr(self, 'user') else None,
                        action='deleted',
                        data=data,
                    )
                except Exception:
                    import traceback

                    traceback.print_exc()
        except Exception:
            import traceback

            traceback.print_exc()
        return None


class BookingImage(models.Model):
    """
    booking is a ForeignKey to the Booking model.
    image is a CloudinaryField to store the image.
    """
    booking = models.ForeignKey(Booking, related_name='images', on_delete=models.CASCADE)
    image = CloudinaryField('image')

    def __str__(self):
        return f"Image for booking {self.booking.id}"


class Cancellation(models.Model):
    """
    Cancellation of a booking with reason and timestamp.
    """
    booking = models.OneToOneField(Booking, related_name='cancellation', on_delete=models.CASCADE)
    reason = models.TextField()
    canceled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cancellation of booking {self.booking.id}"


class BookingHistory(models.Model):
    """
    Tracks changes to Booking.
    """
    ACTIONS = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
    ]

    booking = models.ForeignKey(Booking, null=True, blank=True, on_delete=models.SET_NULL, related_name='history')
    booking_pk = models.IntegerField()
    user = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=10, choices=ACTIONS)
    timestamp = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_action_display()} booking {self.booking_pk} at {self.timestamp.isoformat()}"
    
