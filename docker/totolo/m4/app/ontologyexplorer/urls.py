from django.conf.urls import url, include
from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register('listthemes', views.ThemeViewSet)


urlpatterns = [
    path('', views.index, name='index'),
    url('^api/', include(router.urls)),
    path('themes', views.themes, name='themes'),
    path('test', views.test, name='test'),
]



