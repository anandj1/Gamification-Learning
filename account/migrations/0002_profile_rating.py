# Generated by Django 3.2.13 on 2022-05-04 04:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='rating',
            field=models.FloatField(default=0),
        ),
    ]
