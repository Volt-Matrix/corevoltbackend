# Generated by Django 5.2.1 on 2025-05-30 04:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corevolthrm', '0013_merge_0010_worksession_break_0012_merge_20250529_1719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profiles',
            name='alt_phone',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
