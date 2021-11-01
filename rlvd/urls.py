from django.contrib import admin
from django.urls import path, include

from anpr.views import exportExcel
from . import views

urlpatterns = [path("", views.index), 
                path("platesearch/", views.plate_search),
                # path("getViolations/", views.get_violations),
                path("export/", views.export_csv),
                path("exportExcel/", views.exportExcel),
                path("updateViolations/", views.update_violations),
                # path("dev/", views.dev)
                ]
