import uuid

from django.db import models
from django.urls import reverse


# Create your models here.
class Film(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()
    year = models.IntegerField()
    genre = models.CharField(max_length=150)
    rating = models.FloatField()
    countries = models.CharField(max_length=150)
    poster = models.TextField(blank=True)
    movie_length = models.IntegerField(default=0)
    series_length = models.IntegerField(default=0)
    slug = models.SlugField(default=False)
    def __str__(self):
        return self.name
    def get_absolute_urls(self):
        return reverse("more", kwargs={"film_slug":self.slug, "number":self.id})

class Categories(models.Model):
    name = models.CharField(max_length=120)
    def __str__(self):
        return self.name
    def get_absolute_urls(self):
       return reverse("films_ct", kwargs={"category_name":self.name})
class Films_with_Categories(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()
    year = models.IntegerField()
    genre = models.CharField(max_length=150)
    rating = models.FloatField()
    countries = models.CharField(max_length=150)
    poster = models.TextField(blank=True)
    movie_length = models.IntegerField(default=0)
    series_length = models.IntegerField(default=0)
    slug = models.SlugField(default=False)
    category = models.ForeignKey("Categories", on_delete=models.PROTECT)
    def __str__(self):
        return self.name
    def get_absolute(self):
        return reverse("more", kwargs={"film_slug":self.slug,"number":0})

