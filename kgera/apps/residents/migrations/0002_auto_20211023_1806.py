# Generated by Django 3.2.8 on 2021-10-23 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('residents', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='communityheads',
            name='date_relieved',
            field=models.DateField(null=True, verbose_name='end_date'),
        ),
        migrations.AlterField(
            model_name='residents',
            name='occupancy_end',
            field=models.DateField(null=True, verbose_name='occ_end'),
        ),
    ]
