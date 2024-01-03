from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^dentistas/$', views.DentistaList.as_view(), name='dentista-list'),
]