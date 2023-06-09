# Generated by Django 4.1.7 on 2023-04-20 03:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Submitted', 'Submitted'), ('Confirmed', 'Confirmed'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered'), ('Return', 'Return'), ('Cancel', 'Cancel'), ('Cancelled', 'Cancelled')], default='Submitted', max_length=30),
        ),
    ]
