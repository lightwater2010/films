from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.text import slugify
from django.views.generic import ListView, DetailView
import requests
import json
from translate import Translator
from kino_search.models import *

from kino_search.utils import MyMixin


# Create your views here.
class home(ListView, MyMixin):
    template_name = "kino_search/home.html"
    model = Film

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context2 = self.get_context(title="Главная")
        return dict(list(context.items())+list(context2.items()))


class Search(ListView,MyMixin):
    template_name = "kino_search/home.html"
    context_object_name = "films"
    model = Film
    paginate_by = 2
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        with open("film.json", "r", encoding="utf-8") as file:
            data_films = json.load(file)
            film_name2 = data_films["film_name"]
        context2 = self.get_context(title="Найденное",result_of_search=Film.objects.filter(name__contains=film_name2.lower()).count())

        return dict(list(context.items())+list(context2.items()))
    def get_queryset(self):
        film_name = self.request.GET.get("q")
        input_data = {"film_name":film_name}

        if film_name:
            with open("film.json", "w", encoding="utf-8") as file:
                json.dump(input_data, file)
        with open("film.json", "r", encoding="utf-8") as file:
            dict_json = json.load(file)
            film_name2 = dict_json["film_name"]

        Film.objects.all().delete()
        request = requests.get(f"https://api.kinopoisk.dev/v1.4/movie/search?query={film_name2}", headers={"X-API-KEY": "9KCF0F8-CK24S4Z-HMW0EKB-4QGZ8WN"}).json()
        print(requests)
        films = request.get("docs")
        if not films:
            return "Такого фильма нет..."
        else:
            translater = Translator(from_lang="ru", to_lang="en")
            for i in films:
                genres = []
                countries = []
                for genre in i["genres"]:
                    genres.append(genre["name"])
                for country in i["countries"]:
                    countries.append(country["name"])
                if i["poster"] and i["ageRating"] and i["seriesLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))


                    Film.objects.create(name=f'{i["name"].lower()} {str(i["ageRating"])}+',description=i["description"], year=int(i["year"]),genre=','.join(genres), rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster=i["poster"]["url"],movie_length=0,series_length=i["seriesLength"],slug=film_slug)

                elif i["poster"] and i["ageRating"] and i["movieLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))
                    Film.objects.create(name=f'{i["name"].lower()} {str(i["ageRating"])}+', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                        rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster=i["poster"]["url"], movie_length=i["movieLength"],series_length=0,slug=film_slug)
                elif not i["poster"] and not i["ageRating"] and i["movieLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))
                    Film.objects.create(name=f'{i["name"].lower()}', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                        rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster="-", movie_length=i["movieLength"], series_length=0,
                                        slug=film_slug)
                elif not i["poster"] and not i["ageRating"] and i["seriesLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))
                    Film.objects.create(name=f'{i["name"].lower()}', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                        rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster="-", movie_length=0, series_length=i["seriesLength"],
                                        slug=film_slug)
            return Film.objects.filter(name__contains=film_name2.lower())
class More(DetailView):
    template_name = "kino_search/more.html"
    model = Film
    context_object_name = "film"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = context["film"]
        return context
    def get_object(self, queryset=None):
        if self.kwargs["number"] != 0:
            return Film.objects.get(slug=self.kwargs["film_slug"],id=self.kwargs["number"])
        else:
            return Films_with_Categories.objects.get(slug=self.kwargs["film_slug"])
class Films_with_Categories_Page(ListView,MyMixin):
    model = Films_with_Categories
    template_name = "kino_search/films_with_ct.html"
    context_object_name = "films"
    paginate_by = 2
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context2 = self.get_context(title=str(context["films"][0].category),amount_result=Films_with_Categories.objects.all().count())

        return dict(list(context.items())+list(context2.items()))
    def get_queryset(self):
        Films_with_Categories.objects.all().delete()
        if self.kwargs["category_name"] == "Мелодрама":
            request = requests.get(f"https://api.kinopoisk.dev/v1.4/movie?genres.name=мелодрама", headers={"X-API-KEY": "9KCF0F8-CK24S4Z-HMW0EKB-4QGZ8WN"}).json()
            films = request.get("docs")
            translater = Translator(from_lang="ru", to_lang="en")
            for i in films:
                genres = []
                countries = []
                for genre in i["genres"]:
                    genres.append(genre["name"])
                for country in i["countries"]:
                    countries.append(country["name"])
                if i["poster"] and i["ageRating"] and i["seriesLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))

                    Films_with_Categories.objects.create(name=f'{i["name"].lower()} {str(i["ageRating"])}+', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                        rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster=i["poster"]["url"], movie_length=0, series_length=i["seriesLength"],
                                        slug=film_slug,category_id=1)

                elif i["poster"] and i["ageRating"] and i["movieLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))
                    Films_with_Categories.objects.create(name=f'{i["name"].lower()} {str(i["ageRating"])}+', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                        rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster=i["poster"]["url"], movie_length=i["movieLength"], series_length=0, slug=film_slug, category_id=1)
                elif not i["poster"] and not i["ageRating"] and i["movieLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))
                    Films_with_Categories.objects.create(name=f'{i["name"].lower()}', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                        rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster="-", movie_length=i["movieLength"], series_length=0,
                                        slug=film_slug,category_id=1)
                elif not i["poster"] and not i["ageRating"] and i["seriesLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))
                    Films_with_Categories.objects.create(name=f'{i["name"].lower()}', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                        rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster="-", movie_length=0, series_length=i["seriesLength"],
                                        slug=film_slug,category_id=1)
            return Films_with_Categories.objects.filter(category__name="Мелодрама")
        elif self.kwargs['category_name'] == "Ужасы":
            request = requests.get(f"https://api.kinopoisk.dev/v1.4/movie?genres.name=ужасы", headers={"X-API-KEY": "9KCF0F8-CK24S4Z-HMW0EKB-4QGZ8WN"}).json()
            films = request.get("docs")
            translater = Translator(from_lang="ru", to_lang="en")
            for i in films:
                genres = []
                countries = []
                for genre in i["genres"]:
                    genres.append(genre["name"])
                for country in i["countries"]:
                    countries.append(country["name"])
                if i["poster"] and i["ageRating"] and i["seriesLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))

                    Films_with_Categories.objects.create(name=f'{i["name"].lower()} {str(i["ageRating"])}+', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                                         rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster=i["poster"]["url"], movie_length=0,
                                                         series_length=i["seriesLength"],
                                                         slug=film_slug, category_id=2)

                elif i["poster"] and i["ageRating"] and i["movieLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))
                    Films_with_Categories.objects.create(name=f'{i["name"].lower()} {str(i["ageRating"])}+', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                                         rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster=i["poster"]["url"], movie_length=i["movieLength"],
                                                         series_length=0, slug=film_slug, category_id=2)
                elif not i["poster"] and not i["ageRating"] and i["movieLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))
                    Films_with_Categories.objects.create(name=f'{i["name"].lower()}', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                                         rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster="-", movie_length=i["movieLength"], series_length=0,
                                                         slug=film_slug, category_id=2)
                elif not i["poster"] and not i["ageRating"] and i["seriesLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))
                    Films_with_Categories.objects.create(name=f'{i["name"].lower()}', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                                         rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster="-", movie_length=0, series_length=i["seriesLength"],
                                                         slug=film_slug, category_id=2)
            return Films_with_Categories.objects.filter(category__name="Ужасы")
        elif self.kwargs["category_name"] == "Боевик":
            request = requests.get(f"https://api.kinopoisk.dev/v1.4/movie?genres.name=боевик", headers={"X-API-KEY": "9KCF0F8-CK24S4Z-HMW0EKB-4QGZ8WN"}).json()
            films = request.get("docs")
            translater = Translator(from_lang="ru", to_lang="en")
            for i in films:
                genres = []
                countries = []
                for genre in i["genres"]:
                    genres.append(genre["name"])
                for country in i["countries"]:
                    countries.append(country["name"])
                if i["poster"] and i["ageRating"] and i["seriesLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))

                    Films_with_Categories.objects.create(name=f'{i["name"].lower()} {str(i["ageRating"])}+', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                                         rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster=i["poster"]["url"], movie_length=0,
                                                         series_length=i["seriesLength"],
                                                         slug=film_slug, category_id=3)

                elif i["poster"] and i["ageRating"] and i["movieLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))
                    Films_with_Categories.objects.create(name=f'{i["name"].lower()} {str(i["ageRating"])}+', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                                         rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster=i["poster"]["url"], movie_length=i["movieLength"],
                                                         series_length=0, slug=film_slug, category_id=3)
                elif not i["poster"] and not i["ageRating"] and i["movieLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))
                    Films_with_Categories.objects.create(name=f'{i["name"].lower()}', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                                         rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster="-", movie_length=i["movieLength"], series_length=0,
                                                         slug=film_slug, category_id=3)
                elif not i["poster"] and not i["ageRating"] and i["seriesLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))
                    Films_with_Categories.objects.create(name=f'{i["name"].lower()}', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                                         rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster="-", movie_length=0, series_length=i["seriesLength"],
                                                         slug=film_slug, category_id=3)
            return Films_with_Categories.objects.filter(category__name="Боевик")
        elif self.kwargs["category_name"] == "Комедия":
            request = requests.get(f"https://api.kinopoisk.dev/v1.4/movie?genres.name=комедия", headers={"X-API-KEY": "9KCF0F8-CK24S4Z-HMW0EKB-4QGZ8WN"}).json()
            films = request.get("docs")
            translater = Translator(from_lang="ru", to_lang="en")
            for i in films:
                genres = []
                countries = []
                for genre in i["genres"]:
                    genres.append(genre["name"])
                for country in i["countries"]:
                    countries.append(country["name"])
                if i["poster"] and i["ageRating"] and i["seriesLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))

                    Films_with_Categories.objects.create(name=f'{i["name"].lower()} {str(i["ageRating"])}+', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                                         rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster=i["poster"]["url"], movie_length=0,
                                                         series_length=i["seriesLength"],
                                                         slug=film_slug, category_id=4)

                elif i["poster"] and i["ageRating"] and i["movieLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))
                    Films_with_Categories.objects.create(name=f'{i["name"].lower()} {str(i["ageRating"])}+', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                                         rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster=i["poster"]["url"], movie_length=i["movieLength"],
                                                         series_length=0, slug=film_slug, category_id=4)
                elif not i["poster"] and not i["ageRating"] and i["movieLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))
                    Films_with_Categories.objects.create(name=f'{i["name"].lower()}', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                                         rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster="-", movie_length=i["movieLength"], series_length=0,
                                                         slug=film_slug, category_id=4)
                elif not i["poster"] and not i["ageRating"] and i["seriesLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))
                    Films_with_Categories.objects.create(name=f'{i["name"].lower()}', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                                         rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster="-", movie_length=0, series_length=i["seriesLength"],
                                                         slug=film_slug, category_id=4)
            return Films_with_Categories.objects.filter(category__name="Комедия")
        elif self.kwargs["category_name"] == "Детектив":
            request = requests.get(f"https://api.kinopoisk.dev/v1.4/movie?genres.name=детектив", headers={"X-API-KEY": "9KCF0F8-CK24S4Z-HMW0EKB-4QGZ8WN"}).json()
            films = request.get("docs")
            translater = Translator(from_lang="ru", to_lang="en")
            for i in films:
                genres = []
                countries = []
                for genre in i["genres"]:
                    genres.append(genre["name"])
                for country in i["countries"]:
                    countries.append(country["name"])
                if i["poster"] and i["ageRating"] and i["seriesLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))

                    Films_with_Categories.objects.create(name=f'{i["name"].lower()} {str(i["ageRating"])}+', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                                         rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster=i["poster"]["url"], movie_length=0,
                                                         series_length=i["seriesLength"],
                                                         slug=film_slug, category_id=5)

                elif i["poster"] and i["ageRating"] and i["movieLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))
                    Films_with_Categories.objects.create(name=f'{i["name"].lower()} {str(i["ageRating"])}+', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                                         rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster=i["poster"]["url"], movie_length=i["movieLength"],
                                                         series_length=0, slug=film_slug, category_id=5)
                elif not i["poster"] and not i["ageRating"] and i["movieLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))
                    Films_with_Categories.objects.create(name=f'{i["name"].lower()}', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                                         rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster="-", movie_length=i["movieLength"], series_length=0,
                                                         slug=film_slug, category_id=5)
                elif not i["poster"] and not i["ageRating"] and i["seriesLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))
                    Films_with_Categories.objects.create(name=f'{i["name"].lower()}', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                                         rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster="-", movie_length=0, series_length=i["seriesLength"],
                                                         slug=film_slug, category_id=5)
            return Films_with_Categories.objects.filter(category__name="Детектив")
        elif self.kwargs["category_name"] == "Фантастика":
            request = requests.get(f"https://api.kinopoisk.dev/v1.4/movie?genres.name=фантастика", headers={"X-API-KEY": "9KCF0F8-CK24S4Z-HMW0EKB-4QGZ8WN"}).json()
            films = request.get("docs")
            translater = Translator(from_lang="ru", to_lang="en")
            for i in films:
                genres = []
                countries = []
                for genre in i["genres"]:
                    genres.append(genre["name"])
                for country in i["countries"]:
                    countries.append(country["name"])
                if i["poster"] and i["ageRating"] and i["seriesLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))

                    Films_with_Categories.objects.create(name=f'{i["name"].lower()} {str(i["ageRating"])}+', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                                         rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster=i["poster"]["url"], movie_length=0,
                                                         series_length=i["seriesLength"],
                                                         slug=film_slug, category_id=6)

                elif i["poster"] and i["ageRating"] and i["movieLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))
                    Films_with_Categories.objects.create(name=f'{i["name"].lower()} {str(i["ageRating"])}+', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                                         rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster=i["poster"]["url"], movie_length=i["movieLength"],
                                                         series_length=0, slug=film_slug, category_id=6)
                elif not i["poster"] and not i["ageRating"] and i["movieLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))
                    Films_with_Categories.objects.create(name=f'{i["name"].lower()}', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                                         rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster="-", movie_length=i["movieLength"], series_length=0,
                                                         slug=film_slug, category_id=6)
                elif not i["poster"] and not i["ageRating"] and i["seriesLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))
                    Films_with_Categories.objects.create(name=f'{i["name"].lower()}', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                                         rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster="-", movie_length=0, series_length=i["seriesLength"],
                                                         slug=film_slug, category_id=6)
            return Films_with_Categories.objects.filter(category__name="Фантастика")
        elif self.kwargs["category_name"] == "Криминал":
            request = requests.get(f"https://api.kinopoisk.dev/v1.4/movie?genres.name=криминал", headers={"X-API-KEY": "9KCF0F8-CK24S4Z-HMW0EKB-4QGZ8WN"}).json()
            films = request.get("docs")
            translater = Translator(from_lang="ru", to_lang="en")
            for i in films:
                genres = []
                countries = []
                for genre in i["genres"]:
                    genres.append(genre["name"])
                for country in i["countries"]:
                    countries.append(country["name"])
                if i["poster"] and i["ageRating"] and i["seriesLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))

                    Films_with_Categories.objects.create(name=f'{i["name"].lower()} {str(i["ageRating"])}+', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                                         rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster=i["poster"]["url"], movie_length=0,
                                                         series_length=i["seriesLength"],
                                                         slug=film_slug, category_id=7)

                elif i["poster"] and i["ageRating"] and i["movieLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))
                    Films_with_Categories.objects.create(name=f'{i["name"].lower()} {str(i["ageRating"])}+', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                                         rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster=i["poster"]["url"], movie_length=i["movieLength"],
                                                         series_length=0, slug=film_slug, category_id=7)
                elif not i["poster"] and not i["ageRating"] and i["movieLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))
                    Films_with_Categories.objects.create(name=f'{i["name"].lower()}', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                                         rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster="-", movie_length=i["movieLength"], series_length=0,
                                                         slug=film_slug, category_id=7)
                elif not i["poster"] and not i["ageRating"] and i["seriesLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))
                    Films_with_Categories.objects.create(name=f'{i["name"].lower()}', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                                         rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster="-", movie_length=0, series_length=i["seriesLength"],
                                                         slug=film_slug, category_id=7)
            return Films_with_Categories.objects.filter(category__name="Криминал")
        elif self.kwargs['category_name'] == "Драма":
            request = requests.get(f"https://api.kinopoisk.dev/v1.4/movie?genres.name=драма", headers={"X-API-KEY": "9KCF0F8-CK24S4Z-HMW0EKB-4QGZ8WN"}).json()
            films = request.get("docs")
            translater = Translator(from_lang="ru", to_lang="en")
            for i in films:
                genres = []
                countries = []
                for genre in i["genres"]:
                    genres.append(genre["name"])
                for country in i["countries"]:
                    countries.append(country["name"])
                if i["poster"] and i["ageRating"] and i["seriesLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))

                    Films_with_Categories.objects.create(name=f'{i["name"].lower()} {str(i["ageRating"])}+', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                                         rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster=i["poster"]["url"], movie_length=0,
                                                         series_length=i["seriesLength"],
                                                         slug=film_slug, category_id=8)

                elif i["poster"] and i["ageRating"] and i["movieLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))
                    Films_with_Categories.objects.create(name=f'{i["name"].lower()} {str(i["ageRating"])}+', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                                         rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster=i["poster"]["url"], movie_length=i["movieLength"],
                                                         series_length=0, slug=film_slug, category_id=8)
                elif not i["poster"] and not i["ageRating"] and i["movieLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))
                    Films_with_Categories.objects.create(name=f'{i["name"].lower()}', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                                         rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster="-", movie_length=i["movieLength"], series_length=0,
                                                         slug=film_slug, category_id=8)
                elif not i["poster"] and not i["ageRating"] and i["seriesLength"]:
                    if i["name"] == "Париж":
                        film_slug = "paris"
                    elif i["name"] == "Унесённые ветром":
                        film_slug = "gone-wind"
                    else:
                        film_slug = slugify(translater.translate(i["name"]))
                    Films_with_Categories.objects.create(name=f'{i["name"].lower()}', description=i["description"], year=int(i["year"]), genre=','.join(genres),
                                                         rating=round(float(i["rating"]["kp"]), 1), countries=','.join(countries), poster="-", movie_length=0, series_length=i["seriesLength"],
                                                         slug=film_slug, category_id=8)
            return Films_with_Categories.objects.filter(category__name="Драма")