# Generated by Django 4.1.6 on 2023-08-22 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appscenter', '0082_alter_app_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='app',
            name='file',
            field=models.FileField(upload_to='static/files/2023-08-22_09-45-50'),
        ),
    ]
