from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [path("", views.getInitialData), 
                path("platesearch/", views.plate_search),
                path("exportDataLength/", views.getExportDataLength),
                path("exportExcelv1/", views.exportExcelv1),
                path("exportExcelv2/", views.exportExcelv2),
                path("updateViolations/", views.update_violations),
                ]
