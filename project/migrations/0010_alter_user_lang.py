# Generated by Django 4.1.1 on 2023-06-27 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0009_rename_alpha_lang_alpha2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='lang',
            field=models.CharField(blank=True, default='en', max_length=2, null=True, verbose_name='Language'),
        ),
    ]