from django.urls import path
from . import views

urlpatterns = [
    path('', views.Scanner.as_view(), name='scanner'),
]
