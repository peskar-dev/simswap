# Generated by Django 5.0.1 on 2024-01-23 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('image_file', models.ImageField(upload_to='images/')),
            ],
        ),
        migrations.RenameField(
            model_name='video',
            old_name='video',
            new_name='video_file',
        ),
        migrations.RemoveField(
            model_name='video',
            name='uploaded_at',
        ),
    ]
