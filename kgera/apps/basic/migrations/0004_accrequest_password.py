# Generated by Django 3.2.8 on 2021-12-03 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basic', '0003_alter_accrequest_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='accrequest',
            name='password',
            field=models.CharField(default='kgera', max_length=50),
        ),
    ]
