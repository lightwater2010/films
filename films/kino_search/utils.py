from kino_search.models import Categories

class MyMixin:
    def get_context(self, **kwargs):
        context = kwargs
        context["genres"] = Categories.objects.all()
        return context