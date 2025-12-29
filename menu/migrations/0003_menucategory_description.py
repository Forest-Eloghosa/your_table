from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0002_add_allergens'),
    ]

    operations = [
        migrations.AddField(
            model_name='menucategory',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
