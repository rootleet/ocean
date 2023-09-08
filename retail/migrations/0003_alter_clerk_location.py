# Generated by Django 4.1.6 on 2023-09-08 06:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0139_alter_bulksms_file'),
        ('retail', '0002_alter_clerk_img'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clerk',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_panel.locations'),
            preserve_default=False,
        ),
    ]
