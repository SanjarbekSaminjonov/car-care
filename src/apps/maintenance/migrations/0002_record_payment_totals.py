from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("maintenance", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="maintenancerecord",
            name="paid_by_label",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="maintenancerecord",
            name="total_amount",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=14),
        ),
    ]
