from django.urls import path
from . import views
urlpatterns = [
    path("", views.initialData ),
    path("platesearch/", views.plate_search),
    path("getLatestEntries/", views.getCameraLatestEntriesAndRecognitions),
    path("debug/", views.debug),
    # path("plate/", views.plate_search1),
    path("feed/", views.camerafeed),
    path("exportExcelv1/", views.exportExcelv1),
    path("exportExcelv2/", views.exportExcelv2),
]





