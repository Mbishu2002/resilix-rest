# Generated by Django 4.2.7 on 2023-11-15 23:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_rename_date_time_of_alert_disasterfeedback_date_time_of_feedback'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='otp',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
