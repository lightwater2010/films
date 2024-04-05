from django.urls import path

from .views import *

urlpatterns = [
    path("", home.as_view(), name="home"),
    path("search/",Search.as_view(),name="search"),
    path("more/<slug:film_slug>/<int:number>/", More.as_view(), name="more"),
    path("categories/<str:category_name>/", Films_with_Categories_Page.as_view(), name="films_ct")
]