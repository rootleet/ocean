# Generated by Django 3.2.13 on 2022-08-14 06:10

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0002_questions'),
    ]

    operations = [
        migrations.AddField(
            model_name='questions',
            name='uni',
            field=models.TextField(default=django.utils.timezone.now, unique=True),
            preserve_default=False,
        ),
    ]
