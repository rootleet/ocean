# Generated by Django 4.1.6 on 2023-08-06 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appscenter', '0048_alter_app_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='app',
            name='file',
            field=models.FileField(upload_to='static/files/2023-08-06_11-56-03'),
        ),
    ]
