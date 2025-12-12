# Generated manually

import django.db.models.deletion

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("tracking", "0002_remove_tracking_token_token"),
    ]

    operations = [
        # Add last_used field to Token
        migrations.AddField(
            model_name="token",
            name="last_used",
            field=models.DateTimeField(blank=True, null=True),
        ),
        # Add token field to TrackingData
        # Note: If you have existing TrackingData records, you'll need to:
        # 1. Add this field as nullable first (null=True)
        # 2. Create a data migration to populate existing records
        # 3. Then make it non-nullable
        migrations.AddField(
            model_name="trackingdata",
            name="token",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="trackingdata_entries",
                to="tracking.token",
                null=True,  # Set to False if no existing data, or after data migration
            ),
        ),
        # Add token field to NotificationData
        migrations.AddField(
            model_name="notificationdata",
            name="token",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="notificationdata_entries",
                to="tracking.token",
                null=True,  # Set to False if no existing data, or after data migration
            ),
        ),
        # Add token field to InterceptionData
        migrations.AddField(
            model_name="interceptiondata",
            name="token",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="interceptiondata_entries",
                to="tracking.token",
                null=True,  # Set to False if no existing data, or after data migration
            ),
        ),
    ]
