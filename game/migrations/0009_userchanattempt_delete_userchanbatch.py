# Generated by Django 4.1.1 on 2022-12-04 21:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('game', '0008_rename_time_userchanbatch_created'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserChanAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('mode', models.CharField(choices=[('easy', 'Easy'), ('normal', 'Normal'), ('hard', 'Hard')], default='normal', max_length=6)),
                ('is_solved', models.BooleanField(default=False)),
                ('is_pending', models.BooleanField(default=True)),
                ('chan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.chan')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='UserChanBatch',
        ),
    ]
