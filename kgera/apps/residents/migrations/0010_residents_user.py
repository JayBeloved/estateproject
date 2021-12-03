# Generated by Django 3.2.8 on 2021-12-03 09:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_profile_house'),
        ('residents', '0009_alter_residents_occupancy_start'),
    ]

    operations = [
        migrations.AddField(
            model_name='residents',
            name='user',
            field=models.ForeignKey(default='kgera', on_delete=django.db.models.deletion.CASCADE, to='accounts.user', to_field='username'),
        ),
    ]