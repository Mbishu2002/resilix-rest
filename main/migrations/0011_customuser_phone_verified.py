# Generated by Django 4.2.7 on 2024-07-07 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_alter_customuser_notify_via_sms'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='phone_verified',
            field=models.BooleanField(default=False),
        ),
    ]
