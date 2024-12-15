# Generated by Django 5.1.4 on 2024-12-12 06:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BusStop',
            fields=[
                ('stop_id', models.AutoField(primary_key=True, serialize=False)),
                ('location', models.CharField(max_length=200)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='SystemLog',
            fields=[
                ('log_id', models.AutoField(primary_key=True, serialize=False)),
                ('event_type', models.CharField(max_length=100)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('details', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('preferences', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CongestionData',
            fields=[
                ('record_id', models.AutoField(primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('student_count', models.IntegerField()),
                ('congestion_level', models.CharField(max_length=50)),
                ('stop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.busstop')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('notification_id', models.AutoField(primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('message', models.TextField()),
                ('stop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.busstop')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.user')),
            ],
        ),
    ]