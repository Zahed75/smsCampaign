# Generated by Django 5.1.6 on 2025-03-06 06:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0004_rename_name_customer_customer_name_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CustomerGiftSelection',
        ),
        migrations.DeleteModel(
            name='GiftCard',
        ),
    ]
