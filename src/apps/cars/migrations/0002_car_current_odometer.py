from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cars", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="car",
            name="current_odometer",
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
    ]
