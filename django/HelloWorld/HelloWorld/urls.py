from django.conf.urls import url
from django.urls import path
from django.http import HttpResponse
from django.views.generic.base import TemplateView
 
from . import view
 
urlpatterns = [
    path('api/test/'        , view.test),
    path('api/search/'      , view.search),
    path('api/show/'        , view.show),
    path('api/transmit/'    , view.transmit),
    path('api/clicks/'      , view.clicks),
    path('api/recommend/'   , view.recommend),
]