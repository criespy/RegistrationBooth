from django.urls import path
from . import views
from .views import tamu_update_view

urlpatterns = [
    path('', views.Scanner.as_view(), name='scanner'),
    path('checkin/<slug:slug>', views.CheckInView.as_view(), name='checkin'),
    path('list-tamu/', views.TamuListView.as_view(), name='list-tamu'),
    path('list-tamu-edit/', views.TamuEditListView.as_view(), name='list-tamu-edit'),
    path('login/', views.RegistrationLoginView.as_view(), name='login'),
    path('logout/', views.RegistrationLogoutView.as_view(), name='logout'),
    path('tamu-update/', tamu_update_view, name='tamu-update'),
    path('tamu/edit/<int:pk>/', views.TamuUpdateView.as_view(), name='tamu-edit'),
    path('tamu-create/', views.TamuCreateView.as_view(), name='tamu-create'),
    path('tamu-create/event/<int:event_id>/', views.TamuCreateView.as_view(), name='tamu-create-with-event'),
    path('meja-create/', views.MejaCreateView.as_view(), name='meja-create'),
    path('meja-list/', views.MejaListView.as_view(), name='meja-list'),
    path('event-create/', views.EventCreateView.as_view(), name='event-create'),
    path('event-update/<int:pk>/', views.EventUpdateView.as_view(), name='event-update'),
    path('event-detail/<int:pk>/', views.EventDetailView.as_view(), name='event-detail'),
    path('event-list/', views.EventListView.as_view(), name='event-list'),
]
