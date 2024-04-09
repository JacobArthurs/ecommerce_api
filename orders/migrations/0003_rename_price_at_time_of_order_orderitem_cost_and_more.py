# Generated by Django 5.0.3 on 2024-03-29 00:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_remove_order_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderitem',
            old_name='price_at_time_of_order',
            new_name='cost',
        ),
        migrations.AddField(
            model_name='order',
            name='total_cost',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]