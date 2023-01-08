from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from rest_framework import viewsets
from .models import Theme
from .serializers import ThemeSerializer

def index(request):
    template = loader.get_template("ontologyexplorer/index.html")
    return HttpResponse(template.render({}, request))

def themes(request):
    template = loader.get_template("ontologyexplorer/themes.html")
    return HttpResponse(template.render({}, request))


def test(request):
    Theme(score=1.0, name="test theme", parents="the human condition", description="whatever").save()
    return HttpResponse("Created one theme")


class ThemeViewSet(viewsets.ModelViewSet):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer

