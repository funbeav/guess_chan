# Generated by Django 4.1.1 on 2023-06-28 21:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0011_alter_user_lang'),
        ('game', '0020_remove_userchanimageattempt_shown_letters_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userchanimageattempt',
            name='answer_lang',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='project.lang'),
        ),
    ]
