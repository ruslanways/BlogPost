# Generated by Django 4.0.6 on 2022-07-11 17:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0003_like_unique_like'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-updated']},
        ),
    ]