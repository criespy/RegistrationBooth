from django.urls import path
from . import views

urlpatterns = [
    path('', views.Scanner.as_view(), name='scanner'),
    path('checkin/<slug:slug>', views.CheckInView.as_view(), name='checkin'),
]
