# Generated by Django 4.1.6 on 2023-07-28 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appscenter', '0034_alter_app_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='app',
            name='file',
            field=models.FileField(upload_to='static/files/2023-07-28_16-10-13'),
        ),
    ]
