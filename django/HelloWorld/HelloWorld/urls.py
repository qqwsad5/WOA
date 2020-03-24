from django.conf.urls import url
from django.urls import path
 
from . import view
 
urlpatterns = [
    path('detail/', view.detail),
    path('search/', view.search),
]