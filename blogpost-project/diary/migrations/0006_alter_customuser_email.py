# Generated by Django 4.0.6 on 2022-07-15 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0005_post_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(blank=True, error_messages={'unique': 'A user with that email already exists.'}, max_length=254, unique=True, verbose_name='email address'),
        ),
    ]
