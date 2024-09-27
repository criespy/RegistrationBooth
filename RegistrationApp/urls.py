from django.urls import path
from . import views
from .views import tamu_update_view

urlpatterns = [
    path('', views.Scanner.as_view(), name='scanner'),
    path('checkin/<slug:slug>', views.CheckInView.as_view(), name='checkin'),
    path('list-tamu/', views.TamuListView.as_view(), name='list-tamu'),
    path('login/', views.RegistrationLoginView.as_view(), name='login'),
    path('logout/', views.RegistrationLogoutView.as_view(), name='logout'),
    path('tamu-update/', tamu_update_view, name='tamu-update'),
]
