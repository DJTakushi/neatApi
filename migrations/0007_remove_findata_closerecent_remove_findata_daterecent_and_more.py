# Generated by Django 4.0 on 2022-09-01 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('neatApi', '0006_findata_currency_findata_previousclose_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='findata',
            name='closeRecent',
        ),
        migrations.RemoveField(
            model_name='findata',
            name='dateRecent',
        ),
        migrations.RemoveField(
            model_name='findata',
            name='openRecent',
        ),
        migrations.RemoveField(
            model_name='findata',
            name='previousCloseRefreshDate',
        ),
        migrations.AddField(
            model_name='findata',
            name='downloadRefreshDate',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='findata',
            name='regularMarketPrice',
            field=models.FloatField(null=True),
        ),
    ]
