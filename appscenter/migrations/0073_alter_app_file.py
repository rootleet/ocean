# Generated by Django 4.1.6 on 2023-08-18 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appscenter', '0072_alter_app_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='app',
            name='file',
            field=models.FileField(upload_to='static/files/2023-08-18_07-16-14'),
        ),
    ]
