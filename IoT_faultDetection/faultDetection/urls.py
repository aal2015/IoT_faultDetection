from django.urls import path
from . import views

urlpatterns = [
    path('hotels/', views.list_hotels),
    path('hotels/<int:hotel_id>/floors/', views.list_floors),
    path('floors/<int:floor_id>/rooms/', views.list_rooms),
    path('active-alarms/', views.active_alarms),
    path('active-fault-alarms/', views.active_fault_alarms),
]