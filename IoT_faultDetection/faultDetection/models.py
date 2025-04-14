from django.db import models

class Hotel(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()

    def __str__(self):
        return self.name

class Floor(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='floors')
    floor_number = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.hotel.name} - Floor {self.floor_number}"

class Room(models.Model):
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=20)

    def __str__(self):
        return f"Room {self.room_number} on {self.floor}"

class Device(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='hotel_devices')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='devices', null=True)
    device_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    sensor_type = models.CharField(max_length=100)  # e.g., 'IAQ', 'POWER'
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class SensorData(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='sensor_data')
    datetime = models.DateTimeField(auto_now_add=True)
    datapoint = models.CharField(max_length=100) # e.g., 'temperature', 'humidity', 'co2'
    value = models.CharField(max_length=100)

    def __str__(self):
        return f"SensorData for {self.device} @ {self.datetime}"

# Default thresholds per sensor type
class SensorTypeFaultDetectionThreshold(models.Model):
    sensor_type = models.CharField(max_length=100)  # e.g., 'IAQ', 'POWER'
    datapoint = models.CharField(max_length=100) # e.g., 'temperature', 'humidity', 'co2'
    min_value = models.FloatField(null=True, blank=True)
    max_value = models.FloatField(null=False, blank=False)

    def __str__(self):
        return f"{self.sensor_type}: {self.datapoint}"

# Device-specific overrides (optional)
class DeviceFaultDetectionThreshold(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='device_thresholds')
    datapoint = models.CharField(max_length=100)  # e.g., 'temperature'
    min_value = models.FloatField(null=True, blank=True)
    max_value = models.FloatField(null=False, blank=False)

    def __str__(self):
        return f"{self.device}: {self.datapoint} Threshold"


class PastFaultAlert(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='past_fault_alerts')
    sensor_data = models.OneToOneField(SensorData, on_delete=models.CASCADE, related_name='past_sensor_point_fault')
    datapoint = models.CharField(max_length=100)
    message = models.TextField()
    triggered_at = models.DateTimeField(auto_now_add=True)
    acknowledged = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"PastFaultAlert from {self.device} ({self.datapoint}) at {self.triggered_at}"

class ActiveFaultAlert(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='active_fault_alerts')
    sensor_data = models.OneToOneField(SensorData, on_delete=models.CASCADE, related_name='active_sensor_point_fault')
    datapoint = models.CharField(max_length=100)
    message = models.TextField()
    triggered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("device", "datapoint")

    def __str__(self):
        return f"ActiveFaultAlert from {self.device} ({self.datapoint}) at {self.triggered_at}"
