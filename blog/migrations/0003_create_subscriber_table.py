from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0002_create_subscriber_table"),
    ]

    operations = [
        # This migration is intentionally left empty.
        # Subscriber table is already created in 0002_create_subscriber_table.
    ]
