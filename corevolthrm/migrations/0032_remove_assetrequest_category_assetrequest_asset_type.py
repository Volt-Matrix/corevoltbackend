# Generated by Django 5.2.1 on 2025-06-26 07:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corevolthrm', '0031_alter_assetrequest_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assetrequest',
            name='category',
        ),
        migrations.AddField(
            model_name='assetrequest',
            name='asset_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='corevolthrm.asset'),
        ),
    ]
