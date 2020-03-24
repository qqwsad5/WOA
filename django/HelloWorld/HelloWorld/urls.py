from django.conf.urls import url
from django.urls import re_path
 
from . import view
 
urlpatterns = [
    re_path(r'\w*/detail/', view.detail),
    re_path(r'\w*/search/', view.search),
]