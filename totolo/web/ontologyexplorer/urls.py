from django.conf.urls import url, include
from django.urls import path
from rest_framework import routers
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

router = routers.DefaultRouter()
router.register('search/stories', views.StoryViewSet)
router.register('search/themes', views.ThemeViewSet)
router.register('search/storythemes', views.StoryThemeViewSet)


urlpatterns = [
    path('', views.index, name='index'),
    url('^api/', include(router.urls)),
    path('stories', views.stories, name='stories'),
    path('themes', views.themes, name='themes'),
    path('data', views.data, name='data'),
    url('story/(?P<sid>.+)$', views.story, name='story'),
    url('theme/(?P<name>.+)$', views.theme, name='theme'),
    url('logs/(?P<name>.+)$', views.logs, name='logname'),
]


urlpatterns += staticfiles_urlpatterns()
