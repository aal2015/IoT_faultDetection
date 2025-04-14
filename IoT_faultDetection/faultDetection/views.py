from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
import json
from .models import *

def list_hotels(request):
    if request.method == 'GET':
        hotels = list(Hotel.objects.values())
        return JsonResponse(hotels, safe=False)

def list_floors(request, hotel_id):
    if request.method == 'GET':
        floors = list(Floor.objects.filter(hotel_id=hotel_id).values())
        return JsonResponse(floors, safe=False)

def list_rooms(request, floor_id):
    if request.method == 'GET':
        rooms = list(Room.objects.filter(floor_id=floor_id).values())
        return JsonResponse(rooms, safe=False)


def active_alarms(request):
    data = []

    # Get all active devices, select related room for efficiency
    devices = Device.objects.filter(is_active=True).select_related('room')

    # Build map from device_id to alert
    alerts = {alert.device_id: alert for alert in ActiveFaultAlert.objects.all()}

    for device in devices:
        alert = alerts.get(device.id)

        data.append({
            "room_no": device.room.room_number if device.room else "N/A",
            "device_type": device.sensor_type,
            "fault_status": 'Fault' if alert else 'Normal',
            "fault_type": alert.message if alert else "-",
            "triggered_at": alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S') if alert else "-"
        })

    return JsonResponse(data, safe=False)

def active_fault_alarms(request):
    data = []

    # Get all active fault alerts, including related device and room
    alerts = ActiveFaultAlert.objects.select_related('device__room')

    for alert in alerts:
        device = alert.device
        room = device.room

        data.append({
            "room_no": room.room_number if room else "N/A",
            "device_type": device.sensor_type,
            "fault_status": "Fault",
            "fault_type": alert.message,
            "triggered_at": alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S'),
        })

    return JsonResponse(data, safe=False)