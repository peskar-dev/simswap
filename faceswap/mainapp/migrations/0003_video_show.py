# Generated by Django 5.0.1 on 2024-01-23 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mainapp", "0002_image_rename_video_video_video_file_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="video",
            name="show",
            field=models.BooleanField(default=False),
        ),
    ]
