# Generated by Django 3.2.13 on 2022-04-27 04:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('suadmin', '0003_eventparticipants'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventparticipants',
            name='event',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='suadmin.event'),
            preserve_default=False,
        ),
    ]
