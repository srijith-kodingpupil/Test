# Generated by Django 3.0.14 on 2021-11-21 05:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_auto_20211121_1114'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listing',
            old_name='img',
            new_name='img_url',
        ),
    ]