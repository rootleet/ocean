# Generated by Django 3.2.13 on 2022-08-18 00:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tags',
            name='provider',
            field=models.IntegerField(default=0),
        ),
    ]
