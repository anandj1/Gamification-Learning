# Generated by Django 5.1.6 on 2025-02-25 16:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_profile_rating'),
        ('student', '0018_flippeddiscussion_flippedreply'),
    ]

    operations = [
        migrations.AddField(
            model_name='flippeddiscussion',
            name='is_resolved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='flippeddiscussion',
            name='replied_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='flipped_replies', to='account.profile'),
        ),
    ]
