# Generated by Django 4.1 on 2022-11-18 06:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('admin_panel', '0070_useraddons_profile_pic'),
    ]

    operations = [
        migrations.CreateModel(
            name='PoHd',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry_no', models.TextField()),
                ('remark', models.TextField()),
                ('created_by', models.IntegerField(default=0)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('edited_on', models.DateTimeField(auto_now=True)),
                ('status', models.IntegerField(default=0)),
                ('loc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_panel.locations')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_panel.suppmaster')),
            ],
        ),
        migrations.CreateModel(
            name='PoTran',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('line', models.IntegerField()),
                ('packing', models.TextField()),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=65)),
                ('total', models.IntegerField()),
                ('entry_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.pohd')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_panel.productmaster')),
            ],
        ),
    ]