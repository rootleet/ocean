# Generated by Django 4.1.6 on 2024-07-04 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appscenter', '0002_alter_app_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='app',
            name='file',
            field=models.FileField(upload_to='static/uploads/apps/2024-07-04_16-58-06'),
        ),
    ]