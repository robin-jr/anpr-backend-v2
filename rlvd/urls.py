from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [path("", views.getInitialData), 
                path("platesearch/", views.plate_search),
                # path("getViolations/", views.get_violations),
                # path("export/", views.export_csv),
                path("exportExcelv1/", views.exportExcelv1),
                path("exportExcelv2/", views.exportExcelv2),
                path("updateViolations/", views.update_violations),
                # path("dev/", views.dev)
                ]
