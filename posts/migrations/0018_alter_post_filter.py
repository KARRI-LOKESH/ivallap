# Generated by Django 5.2 on 2025-05-16 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0017_alter_post_filter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='filter',
            field=models.CharField(choices=[('none', 'Normal'), ('contrast(130%) brightness(110%) saturate(180%)', 'Vibrant Pop'), ('sepia(40%) contrast(120%) brightness(105%)', 'Warm Glow'), ('grayscale(80%) contrast(140%) brightness(90%)', 'Moody B&W'), ('drop-shadow(8px 8px 6px rgba(0,0,0,0.5)) brightness(110%)', 'Shadow Glow'), ('hue-rotate(180deg) saturate(150%) brightness(90%)', 'Cool Tone'), ('brightness(90%) contrast(140%) saturate(150%) sepia(30%)', 'Retro Warmth'), ('brightness(110%) contrast(120%) blur(1px)', 'Dreamy Soft'), ('contrast(160%) saturate(200%) brightness(115%)', 'Ultra Vivid'), ('sepia(100%) contrast(150%) brightness(85%) grayscale(20%)', 'Classic Film'), ('invert(20%) hue-rotate(20deg) saturate(250%)', 'Neon Glow'), ('brightness(150%) contrast(120%) drop-shadow(4px 4px 6px #000)', 'Radiant Light'), ('grayscale(100%)', 'Grayscale'), ('sepia(100%)', 'Sepia'), ('blur(2px)', 'Blur'), ('contrast(150%)', 'High Contrast'), ('brightness(120%)', 'Bright'), ('invert(100%)', 'Invert'), ('hue-rotate(90deg)', 'Hue Rotate'), ('saturate(200%)', 'Saturate'), ('drop-shadow(5px 5px 5px gray)', 'Drop Shadow')], default='none', max_length=100),
        ),
    ]
