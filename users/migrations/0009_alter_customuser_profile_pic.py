# Generated by Django 5.1.7 on 2025-04-10 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_alter_customuser_profile_pic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='profile_pic',
            field=models.ImageField(blank=True, default='profile_pics/default-profile.png', null=True, upload_to='profile_pics/'),
        ),
    ]
