# Generated by Django 4.1.6 on 2024-06-13 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmms', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='proformainvoice',
            name='prospective_email',
            field=models.TextField(default='same'),
        ),
        migrations.AddField(
            model_name='proformainvoice',
            name='prospective_name',
            field=models.TextField(default='same'),
        ),
        migrations.AddField(
            model_name='proformainvoice',
            name='prospective_phone',
            field=models.TextField(default='same'),
        ),
    ]