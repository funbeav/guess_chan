# Generated by Django 4.1.1 on 2022-12-04 23:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0013_alter_userchanimageattempt_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userchanimageattempt',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2022, 12, 4, 23, 55, 23, 564535, tzinfo=datetime.timezone.utc)),
        ),
    ]
