# Generated by Django 3.2.13 on 2022-08-18 05:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0003_questions_tags'),
    ]

    operations = [
        migrations.RenameField(
            model_name='questions',
            old_name='tags',
            new_name='domain',
        ),
    ]
