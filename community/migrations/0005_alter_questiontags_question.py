# Generated by Django 3.2.13 on 2022-08-14 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0004_questiontags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questiontags',
            name='question',
            field=models.TextField(),
        ),
    ]
