# Generated by Django 4.2.7 on 2023-11-29 19:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kino_search', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='film',
            unique_together={('name',)},
        ),
    ]