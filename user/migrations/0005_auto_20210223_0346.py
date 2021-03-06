# Generated by Django 3.1.6 on 2021-02-22 18:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_order_product_stock'),
        ('user', '0004_auto_20210222_2124'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='is_main',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='address',
            name='order',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='order.order'),
        ),
    ]
