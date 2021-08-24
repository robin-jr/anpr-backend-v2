from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [path("register/",views.registration_view),
        path('login/', obtain_auth_token, name="login"), 
        path('logout/', views.logout, name="logout"), 
        path('sample/', views.sample, name="sample"), ]
