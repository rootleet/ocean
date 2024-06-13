# Generated by Django 5.0.6 on 2024-06-13 07:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('inventory', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='App',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logo', models.ImageField(blank=True, default='static/apps/logos/default.png', null=True, upload_to='static/uploads/apps/logos/')),
                ('name', models.TextField()),
                ('uni', models.CharField(max_length=60, unique=True)),
                ('description', models.TextField()),
                ('file', models.FileField(upload_to='static/uploads/apps/2024-06-13_07-38-26')),
                ('root', models.TextField()),
                ('created_date', models.DateField(auto_now_add=True)),
                ('created_time', models.TimeField(auto_now=True)),
                ('status', models.IntegerField(default=1)),
                ('version', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='AppsGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('uni', models.CharField(max_length=60, unique=True)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('created_time', models.TimeField(auto_now=True)),
                ('status', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='AppAssign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.IntegerField(default=0)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('created_time', models.TimeField(auto_now_add=True)),
                ('updated_date', models.DateField(auto_now_add=True)),
                ('updated_time', models.TimeField(auto_now_add=True)),
                ('message', models.TextField(default='NULL')),
                ('last_breath', models.TextField(default='NULL')),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appscenter.app')),
                ('mach', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.computer')),
            ],
        ),
        migrations.CreateModel(
            name='AppContainer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('computers', models.ManyToManyField(to='inventory.computergroup')),
            ],
        ),
        migrations.CreateModel(
            name='AppProviders',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField()),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.TextField()),
                ('country', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='app',
            name='provider',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='appscenter.appproviders'),
        ),
        migrations.CreateModel(
            name='VersionControl',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('version_no', models.IntegerField()),
                ('files', models.FileField(upload_to='static/uploads/appversion')),
                ('created_date', models.DateField(auto_now_add=True)),
                ('created_time', models.TimeField(auto_now=True)),
                ('status', models.IntegerField(default=1)),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appscenter.app')),
            ],
        ),
    ]
