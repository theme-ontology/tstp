from django.http import HttpResponse
from django.template import loader
from rest_framework.response import Response
from rest_framework import status

from rest_framework import viewsets
from .models import Theme, Story
from .serializers import StorySerializer, ThemeSerializer
import totolo.search


def index(request):
    template = loader.get_template("ontologyexplorer/index.html")
    return HttpResponse(template.render({}, request))


def stories(request):
    template = loader.get_template("ontologyexplorer/stories.html")
    return HttpResponse(template.render({}, request))


def themes(request):
    template = loader.get_template("ontologyexplorer/themes.html")
    return HttpResponse(template.render({}, request))


def story(request, sid):
    storyobj = Story.objects.get(sid=sid)
    template = loader.get_template("ontologyexplorer/story.html")
    context = {'storyobj': storyobj}
    return HttpResponse(template.render(context, request))


def theme(request, name):
    themeobj = Theme.objects.get(name=name)
    template = loader.get_template("ontologyexplorer/theme.html")
    context = {'themeobj': themeobj}
    return HttpResponse(template.render(context, request))


def searchthemes(request, query):
    pass


class StoryViewSet(viewsets.ModelViewSet):
    queryset = Story.objects.all()[:20]
    serializer_class = StorySerializer

    """
    def get_queryset(self):
        queryset = None
        if self.request.method == 'GET':
            state_name = self.request.GET.get('q', None)
    """

    def list(self, request):
        query = request.GET.get('query', None)
        if query:
            idx2weight = {t.idx: w for (t, w) in totolo.search.themes(query)}
            query_set = Theme.objects.filter(idx__in=idx2weight.keys())
            serial = self.serializer_class(query_set, many=True, weight_index=idx2weight)
            return Response(serial.data, status=status.HTTP_200_OK)
        else:
            return super().list(request)

class ThemeViewSet(viewsets.ModelViewSet):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer


