# Generated by Django 5.1.7 on 2025-04-11 17:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_message'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Message',
        ),
    ]
