from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('products', '0001_initial')]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_available',
            field=models.BooleanField(default=True, help_text='Uncheck to withdraw a product from sale without deleting order history.'),
        ),
    ]
