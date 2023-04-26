# Generated by Django 4.1.7 on 2023-04-20 12:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0002_coupon'),
        ('store', '0002_size_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='coupon',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='coupon.coupon'),
        ),
    ]