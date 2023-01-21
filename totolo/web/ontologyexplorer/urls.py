from django.conf.urls import url, include
from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register('search/stories', views.StoryViewSet)
router.register('search/themes', views.ThemeViewSet)


urlpatterns = [
    path('', views.index, name='index'),
    url('^api/', include(router.urls)),
    path('stories', views.stories, name='stories'),
    path('themes', views.themes, name='themes'),
    url('story/(?P<sid>.+)$', views.story, name='story'),
    url('theme/(?P<name>.+)$', views.theme, name='theme'),
]



