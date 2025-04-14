import pika, sys, os, json, django, time
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from faultDetection.models import (
    Hotel, Floor, Room, Device, SensorData,
    DeviceFaultDetectionThreshold, SensorTypeFaultDetectionThreshold, ActiveFaultAlert
)

threshold_values = [
    {
        "sensor_type": 'iaq',
        "datapoint": "temperature",
        "max_value": "25"
    },
    {
        "sensor_type": 'iaq',
        "datapoint": "humidity",
        "max_value": "50"
    },
    {
        "sensor_type": 'iaq',
        "datapoint": "co2",
        'max_value': "500"
    },
    {
        "sensor_type": 'power',
        "datapoint": "power",
        "max_value": "5"
    }
]

error_messages = {
    'temperature': 'High temperature',
    'humidity': 'High humidity',
    'co2': 'High CO2 level',
    'power': 'Power spike'
}

def get_or_create_location(hotel_name, address, floor_number, room_number=None):
    hotel, _ = Hotel.objects.get_or_create(name=hotel_name, address=address)
    floor, _ = Floor.objects.get_or_create(hotel=hotel, floor_number=str(floor_number))
    room = Room.objects.get_or_create(floor=floor, room_number=str(room_number))[0] if room_number else None
    return hotel, floor, room

def get_or_create_device(hotel, room, sensor_type):
    device_id = f"{sensor_type}-{hotel.id}-{room.id if room else 'NA'}"
    device, _ = Device.objects.get_or_create(
        device_id=device_id,
        defaults={
            "name": f"{sensor_type.capitalize()} Device",
            "sensor_type": sensor_type,
            "hotel": hotel,
            "room": room,
            "is_active": True
        }
    )
    return device

def save_sensor_data(device, datapoint, value, timestamp_str):
    try:
        time_obj = datetime.strptime(timestamp_str, "%H:%M.%S").time()
        timestamp = datetime.combine(datetime.now().date(), time_obj)
    except ValueError:
        timestamp = datetime.now()

    return SensorData.objects.create(
        device=device,
        datapoint=datapoint,
        value=value,
        datetime=timestamp
    )

def check_fault(device, sensor_type, sensor_data, datapoint, value, timestamp_str):
    if sensor_type == 'power':
        datapoint = 'power'

    if ActiveFaultAlert.objects.filter(device=device, datapoint=datapoint).exists():
        return

    try:
        value = float(value)
    except ValueError:
        return

    threshold = (
        DeviceFaultDetectionThreshold.objects.filter(device=device, datapoint=datapoint).first() or
        SensorTypeFaultDetectionThreshold.objects.filter(sensor_type=sensor_type, datapoint=datapoint).first()
    )
    if not threshold:
        return

    try:
        time_obj = datetime.strptime(timestamp_str, "%H:%M.%S").time()
        timestamp = datetime.combine(datetime.now().date(), time_obj)
    except ValueError:
        timestamp = datetime.now()

    if value > threshold.max_value:
        ActiveFaultAlert.objects.create(
            device=device,
            sensor_data=sensor_data,
            datapoint=datapoint,
            message=error_messages.get(datapoint, "Fault detected"),
            triggered_at=timestamp
        )

def set_sensor_type_threshold(sensor_type, datapoint, min_value, max_value):
    try:
        threshold, created = SensorTypeFaultDetectionThreshold.objects.update_or_create(
            sensor_type=sensor_type,
            datapoint=datapoint,
            defaults={
                'min_value': min_value,
                'max_value': max_value
            }
        )
        if created:
            print(f"[+] Created new threshold for {sensor_type} - {datapoint}")
        else:
            print(f"[~] Updated threshold for {sensor_type} - {datapoint}")
    except Exception as e:
        print(f"[❌] Failed to set threshold: {e}")

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)

        hotel_name = data['hotel_name']
        address = data['address']
        floor_number = data['floor']
        room_number = data.get('room_no')
        datapoint = data['datapoint']
        value = data['value']
        timestamp = data['datetime']
        sensor_type = method.routing_key

        hotel, floor, room = get_or_create_location(hotel_name, address, floor_number, room_number)
        device = get_or_create_device(hotel, room, sensor_type)
        sensor_data = save_sensor_data(device, datapoint, value, timestamp)
        check_fault(device, sensor_type, sensor_data, datapoint, value, timestamp)

        print(f"[✔] Received {sensor_type} data: {body}")

    except Exception as e:
        print(f"[❌] Error processing message: {e}")
        print(f"Message: {body}")
        

def connect_to_rabbitmq():
    params = pika.ConnectionParameters(host='rabbitmq', port=5672)
    while True:
        try:
            connection = pika.BlockingConnection(params)
            print("✅ Connected to RabbitMQ.")
            return connection
        except pika.exceptions.AMQPConnectionError:
            print("⏳ Waiting for RabbitMQ to be ready...")
            time.sleep(2)

def main():
    # Apply thresholds
    for threshold in threshold_values:
        set_sensor_type_threshold(
            sensor_type=threshold["sensor_type"],
            datapoint=threshold["datapoint"],
            min_value=0,  # optional: you can set your own default
            max_value=float(threshold["max_value"])
        )

    connection = connect_to_rabbitmq()
    channel = connection.channel()
    channel.exchange_declare(exchange='sensor_exchange', exchange_type='direct')

    sensor_queues = {
        'iaq': 'iaq_sensor',
        'power': 'power_sensor',
        'presence_sensor': 'presence_sensor'
    }

    for routing_key, queue in sensor_queues.items():
        channel.queue_declare(queue=queue)
        channel.queue_bind(exchange='sensor_exchange', queue=queue, routing_key=routing_key)
        channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)

    print(" [*] Waiting for sensor messages. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user. Shutting down...")
        sys.exit(0)
