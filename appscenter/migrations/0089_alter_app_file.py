# Generated by Django 4.1.6 on 2023-08-23 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appscenter', '0088_alter_app_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='app',
            name='file',
            field=models.FileField(upload_to='static/files/2023-08-23_10-36-43'),
        ),
    ]
