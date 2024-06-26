# Generated by Django 5.0.4 on 2024-04-30 09:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BehaviorIndicator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('level', models.IntegerField(default=1)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='behaviours.behaviorindicator')),
            ],
        ),
        migrations.CreateModel(
            name='BehaviorAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=255)),
                ('points', models.IntegerField()),
                ('indicator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actions', to='behaviours.behaviorindicator')),
            ],
        ),
        migrations.CreateModel(
            name='BehaviorRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('performance', models.IntegerField(verbose_name='Performance Score')),
                ('points', models.IntegerField(editable=False, verbose_name='Points')),
                ('date', models.DateField(verbose_name='Date')),
                ('action', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='behaviours.behavioraction', verbose_name='Action')),
                ('performer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='performed_behaviors', to=settings.AUTH_USER_MODEL, verbose_name='Performer')),
                ('recorder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recorded_behaviors', to=settings.AUTH_USER_MODEL, verbose_name='Recorder')),
            ],
        ),
    ]
