# Generated by Django 4.1.6 on 2023-07-20 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appscenter', '0029_alter_app_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='app',
            name='file',
            field=models.FileField(upload_to='static/files/2023-07-20_12-15-27'),
        ),
    ]
