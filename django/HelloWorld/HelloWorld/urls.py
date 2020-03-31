from django.conf.urls import url
from django.urls import path
from django.http import HttpResponse
from django.views.generic.base import TemplateView
 
from . import view
 
urlpatterns = [
    path('api/detail/', view.detail),
    path('api/search/', view.search),
]