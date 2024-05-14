# Generated by Django 5.0.4 on 2024-04-30 13:23

import django.db.models.deletion
import mptt.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('behaviours', '0002_behaviorindicator_lft_behaviorindicator_rght_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='behaviorindicator',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='behaviours.behaviorindicator'),
        ),
    ]