# Generated by Django 4.0 on 2022-08-31 00:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('neatApi', '0004_alter_neatdata_lastrefresh'),
    ]

    operations = [
        migrations.AlterField(
            model_name='findata',
            name='closeHistoric',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='findata',
            name='closeRecent',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='findata',
            name='dateHistoric',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='findata',
            name='dateRecent',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='findata',
            name='openRecent',
            field=models.FloatField(null=True),
        ),
    ]
