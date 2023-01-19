from django.conf.urls import url, include
from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register('listthemes', views.ThemeViewSet)
router.register('liststories', views.StoryViewSet)


urlpatterns = [
    path('', views.index, name='index'),
    url('api/searchthemes', views.searchthemes, name='searchthemes'),
    url('^api/', include(router.urls)),
    path('stories', views.themes, name='stories'),
    path('themes', views.themes, name='themes'),
    url('story/(?P<sid>.+)$', views.story, name='story'),
    url('theme/(?P<name>.+)$', views.theme, name='theme'),
]



