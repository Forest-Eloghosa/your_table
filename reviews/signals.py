from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.apps import apps
from django.forms.models import model_to_dict
from datetime import date, datetime
from decimal import Decimal
from django.db.models.fields.files import FieldFile


def sanitize_value(v):
    if v is None:
        return None
    if isinstance(v, (str, int, float, bool)):
        return v
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    if isinstance(v, Decimal):
        try:
            return float(v)
        except Exception:
            return str(v)
    if isinstance(v, FieldFile):
        try:
            if v.name:
                try:
                    return v.url
                except Exception:
                    return v.name
            return None
        except Exception:
            return None
    try:
        return str(v)
    except Exception:
        return None


@receiver(post_save)
def review_post_save(sender, instance, created, **kwargs):
    if sender.__name__ != 'Review':
        return
    try:
        ReviewHistory = apps.get_model('reviews', 'ReviewHistory')
        data = model_to_dict(instance, fields=[f.name for f in instance._meta.fields if f.name not in ('id',)])

        data = {k: sanitize_value(v) for k, v in data.items()}
        action = 'created' if created else 'updated'
        rh = ReviewHistory.objects.create(
            review=instance if created else None,
            review_pk=instance.pk,
            user=getattr(instance, 'user', None),
            action=action,
            data=data,
        )
        # created ReviewHistory record (debug prints removed)
    except Exception:
        # Avoid raising during app lifecycle; best-effort logging
        import traceback
        traceback.print_exc()


@receiver(post_delete)
def review_post_delete(sender, instance, **kwargs):
    if sender.__name__ != 'Review':
        return
    try:
        ReviewHistory = apps.get_model('reviews', 'ReviewHistory')
        data = model_to_dict(instance, fields=[f.name for f in instance._meta.fields if f.name not in ('id',)])
        data = {k: sanitize_value(v) for k, v in data.items()}


        rh = ReviewHistory.objects.create(
            review=None,
            review_pk=instance.pk,
            user=getattr(instance, 'user', None),
            action='deleted',
            data=data,
        )
        # created ReviewHistory record (debug prints removed)
    except Exception:
        import traceback
        traceback.print_exc()
