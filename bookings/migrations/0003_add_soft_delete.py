"""Add soft-delete fields to Booking model.

This migration adds `is_deleted` (boolean) and `deleted_at` (datetime) to
the `bookings_booking` table so the soft-delete feature works without SQL errors.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0002_bookinghistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='booking',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
