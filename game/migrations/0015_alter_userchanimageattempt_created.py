# Generated by Django 4.1.1 on 2022-12-05 00:05

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0014_alter_userchanimageattempt_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userchanimageattempt',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]