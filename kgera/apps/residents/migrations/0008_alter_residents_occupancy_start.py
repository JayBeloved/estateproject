# Generated by Django 3.2.8 on 2021-12-01 21:24

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('residents', '0007_auto_20211121_1338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='residents',
            name='occupancy_start',
            field=models.DateField(default=datetime.datetime(2021, 12, 1, 21, 24, 27, 527624, tzinfo=utc), null=True, verbose_name='occ_start'),
        ),
    ]
