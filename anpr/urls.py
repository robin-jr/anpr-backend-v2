from django.urls import path
from . import views


urlpatterns = [
    path("", views.initialDatas ),
    path("platesearch/", views.plate_search),
    path("getLatestEntries/", views.getCameraLatestEntriesAndRecognitions),
    path("feed/", views.camerafeed),
    path("export/", views.export_csv),
    path("exportExcel/", views.exportExcel),
]





