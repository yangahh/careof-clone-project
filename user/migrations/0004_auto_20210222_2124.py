# Generated by Django 3.1.6 on 2021-02-22 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_address_zip_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='zip_code',
            field=models.CharField(max_length=20),
        ),
    ]
