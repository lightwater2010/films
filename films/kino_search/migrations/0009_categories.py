# Generated by Django 4.2.7 on 2023-12-26 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kino_search', '0008_remove_film_length_film_movie_length_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
            ],
        ),
    ]
