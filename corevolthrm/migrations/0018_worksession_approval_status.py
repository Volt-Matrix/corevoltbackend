# Generated by Django 5.2.1 on 2025-06-02 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corevolthrm', '0017_timesheetdetails'),
    ]

    operations = [
        migrations.AddField(
            model_name='worksession',
            name='approval_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending', max_length=20),
        ),
    ]
