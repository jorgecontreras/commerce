# Generated by Django 3.1 on 2020-08-31 01:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_watchlist'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='watchlist',
            unique_together={('user', 'listing')},
        ),
    ]
