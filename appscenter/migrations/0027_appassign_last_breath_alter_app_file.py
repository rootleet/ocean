# Generated by Django 4.1.6 on 2023-07-19 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appscenter', '0026_appassign_message_alter_app_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='appassign',
            name='last_breath',
            field=models.TextField(default='NULL'),
        ),
        migrations.AlterField(
            model_name='app',
            name='file',
            field=models.FileField(upload_to='static/files/2023-07-19_11-17-01'),
        ),
    ]
