from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0003_add_soft_delete'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cancellationpolicy',
            name='restaurant',
        ),
        migrations.RemoveField(
            model_name='feedback',
            name='booking',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='booking',
        ),
        migrations.RemoveField(
            model_name='reservation',
            name='booking',
        ),
        migrations.RemoveField(
            model_name='reservation',
            name='table',
        ),
        migrations.RemoveField(
            model_name='specialoffer',
            name='restaurant',
        ),
        migrations.AlterUniqueTogether(
            name='table',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='table',
            name='restaurant',
        ),
        migrations.DeleteModel(
            name='BookingStatus',
        ),
        migrations.DeleteModel(
            name='CancellationPolicy',
        ),
        migrations.DeleteModel(
            name='Feedback',
        ),
        migrations.DeleteModel(
            name='Payment',
        ),
        migrations.DeleteModel(
            name='Reservation',
        ),
        migrations.DeleteModel(
            name='SpecialOffer',
        ),
        migrations.DeleteModel(
            name='Table',
        ),
    ]
