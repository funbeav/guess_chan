# Generated by Django 4.1.1 on 2022-12-04 21:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0007_userchanbatch_is_solved'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userchanbatch',
            old_name='time',
            new_name='created',
        ),
    ]