# Generated by Django 3.2.14 on 2023-08-27 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users_api', '0008_auto_20230826_1929'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
