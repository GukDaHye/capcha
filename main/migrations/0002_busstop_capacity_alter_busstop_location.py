# Generated by Django 5.1.4 on 2024-12-12 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='busstop',
            name='capacity',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='busstop',
            name='location',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
