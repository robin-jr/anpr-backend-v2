from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [path("", views.index), 
                path("platesearch/", views.plate_search),
                path("getViolations/", views.get_violations),
                path("sample/", views.sample),
                path("updateViolations/", views.update_violations),]
