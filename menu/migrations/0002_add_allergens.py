from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("menu", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="menuitem",
            name="allergens",
            field=models.CharField(
                max_length=255,
                blank=True,
                help_text='Optional comma-separated list of allergens, e.g. "nuts, dairy, soy"',
            ),
        ),
    ]
