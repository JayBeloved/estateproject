# Generated by Django 3.2.8 on 2021-10-22 17:23

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('structure', '0003_alter_communitytype_commtype'),
    ]

    operations = [
        migrations.CreateModel(
            name='PropertyTypes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('property_type', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Residents',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resident_code', models.CharField(max_length=20, unique=True)),
                ('first_name', models.CharField(max_length=25)),
                ('last_name', models.CharField(max_length=30)),
                ('resident_email', models.EmailField(max_length=254)),
                ('mobile_number', models.CharField(max_length=15)),
                ('occupancy_start', models.DateField(default=datetime.date, verbose_name='occ_start')),
                ('occupancy_end', models.DateField(verbose_name='occ_end')),
                ('occupancy_status', models.PositiveSmallIntegerField(choices=[(0, 'Vacated The House'), (1, 'Currently Residing In The House')], default=1, verbose_name='Status of Residency')),
                ('house', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.houses', to_field='housecode')),
            ],
        ),
        migrations.CreateModel(
            name='Properties',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('property_type', models.CharField(max_length=30)),
                ('property_code', models.CharField(max_length=30)),
                ('property_desc', models.TextField()),
                ('resident', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='residents.residents', to_field='resident_code')),
            ],
        ),
        migrations.CreateModel(
            name='CommunityHeads',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_appointed', models.DateField(default=datetime.date, verbose_name='start_date')),
                ('date_relieved', models.DateField(verbose_name='end_date')),
                ('appointment_status', models.PositiveSmallIntegerField(choices=[(0, 'Vacated The House'), (1, 'Currently Residing In The House')], default=1, verbose_name='Status of Appointment')),
                ('community', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.community', to_field='commcode')),
                ('resident', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='residents.residents', to_field='resident_code')),
            ],
        ),
    ]