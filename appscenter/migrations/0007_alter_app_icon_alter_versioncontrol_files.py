# Generated by Django 4.1.6 on 2023-06-13 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appscenter', '0006_remove_appassign_status_appassign_updated_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='app',
            name='icon',
            field=models.FileField(upload_to='static/files/2023-06-13_11-57-50'),
        ),
        migrations.AlterField(
            model_name='versioncontrol',
            name='files',
            field=models.FileField(upload_to='static/uploads/appversion'),
        ),
    ]
