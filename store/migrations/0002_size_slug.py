# Generated by Django 4.1.7 on 2023-04-20 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='size',
            name='slug',
            field=models.SlugField(default=12, max_length=20),
            preserve_default=False,
        ),
    ]