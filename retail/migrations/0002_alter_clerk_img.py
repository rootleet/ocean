# Generated by Django 4.1.6 on 2023-09-08 06:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retail', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clerk',
            name='img',
            field=models.ImageField(default='static/general/img/users/default.png', upload_to='static/general/clerks/'),
        ),
    ]