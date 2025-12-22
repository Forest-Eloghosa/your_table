# Generated migration
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_merge_0002_review_image_0002_reviewhistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='guest_name',
            field=models.CharField(blank=True, help_text='Name for anonymous reviews', max_length=100),
        ),
        migrations.AlterField(
            model_name='review',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='reviewhistory',
            name='action',
            field=models.CharField(choices=[('created', 'Created'), ('updated', 'Updated'), ('deleted', 'Deleted')], max_length=10),
        ),
    ]
