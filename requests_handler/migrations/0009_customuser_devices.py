# Generated by Django 3.2.25 on 2024-10-07 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('otp_totp', '0003_add_timestamps'),
        ('requests_handler', '0008_alter_request_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='devices',
            field=models.ManyToManyField(to='otp_totp.TOTPDevice'),
        ),
    ]
