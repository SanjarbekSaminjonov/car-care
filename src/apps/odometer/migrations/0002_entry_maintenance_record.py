import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("maintenance", "0002_record_payment_totals"),
        ("odometer", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="odometerentry",
            name="maintenance_record",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="odometer_entries",
                to="maintenance.maintenancerecord",
            ),
        ),
    ]
