from django.urls import path
from . import views
urlpatterns = [
    path("", views.initialData ),
    path("platesearch/", views.plate_search),
    path("getLatestEntries/", views.getCameraLatestEntriesAndRecognitions),
    path("feed/", views.camerafeed),
    path("exportDataLengthv1/", views.getExportDataLengthv1),
    path("exportDataLengthv2/", views.getExportDataLengthv2),
    path("exportExcelv1/", views.exportExcelv1),
    path("exportExcelv2/", views.exportExcelv2),
    path("exportToUsbv1/", views.exportToUsbv1),
    path("exportToUsbv2/", views.exportToUsbv2),
    ]





