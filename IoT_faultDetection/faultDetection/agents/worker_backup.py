import pika, sys, os, json, django
from datetime import datetime

# Add the path to the BASE DIR
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Set the settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

# Setup Django
django.setup()

from faultDetection.models import Hotel, Floor, Room, Device, SensorData, DeviceFaultDetectionThreshold, SensorTypeFaultDetectionThreshold, ActiveFaultAlert

def get_or_create_location(hotel_name, address, floor_number, room_number=None):
    hotel, _ = Hotel.objects.get_or_create(name=hotel_name, address=address)
    floor, _ = Floor.objects.get_or_create(hotel=hotel, floor_number=str(floor_number))

    if room_number:
        room, _ = Room.objects.get_or_create(floor=floor, room_number=str(room_number))
    else:
        room = None

    return hotel, floor, room

def get_or_create_device(hotel, room, sensor_type):
    # Create unique ID per type/location
    device_id = f"{sensor_type}-{hotel.id}-{room.id if room else 'NA'}"
    name = f"{sensor_type.capitalize()} Device"

    device, _ = Device.objects.get_or_create(
        device_id=device_id,
        defaults={
            "name": name,
            "sensor_type": sensor_type,
            "hotel": hotel,
            "room": room,
            "is_active": True
        }
    )
    return device

def save_sensor_data(device, datapoint, value, timestamp_str):
    # convert into appropriate datetime format
    try:
        # Parse time part from the string
        time_obj = datetime.strptime(timestamp_str, "%H:%M.%S").time()

        # Combine with today's date
        now = datetime.now()
        timestamp = datetime.combine(now.date(), time_obj)
    except ValueError:
        timestamp = datetime.now()

    sensor_data = SensorData.objects.create(
        device=device,
        datapoint=datapoint,
        value=value,
        datetime=timestamp,
    )

    return sensor_data

error_messages = {
    'temperature': 'High temperature',
    'humidity': 'High humidity',
    'co2': 'High CO2 level',
    'power': 'Power spike'
}

def check_fault(device, sensor_type, sensor_data, datapoint, value, timestamp_str):
    # Normalize datapoint for power sensor
    if sensor_type == 'power':
        datapoint = sensor_type

    # Check if fault is already detected
    if ActiveFaultAlert.objects.filter(device=device, datapoint=datapoint).exists():
        return

    value = float(value)

    # Try to get threshold specific to this device
    try:
        threshold = DeviceFaultDetectionThreshold.objects.get(
            device=device,
            datapoint=datapoint
        )
    except DeviceFaultDetectionThreshold.DoesNotExist:
        # Fall back to global threshold
        try:
            threshold = SensorTypeFaultDetectionThreshold.objects.get(
                sensor_type=sensor_type,
                datapoint=datapoint
            )
        except SensorTypeFaultDetectionThreshold.DoesNotExist:
            # No threshold found at all
            return

    # Convert timestamp
    try:
        time_obj = datetime.strptime(timestamp_str, "%H:%M.%S").time()
        now = datetime.now()
        timestamp = datetime.combine(now.date(), time_obj)
    except ValueError:
        timestamp = datetime.now()

    # Compare value with threshold
    if value > threshold.max_value:
        ActiveFaultAlert.objects.create(
            device=device,
            sensor_data=sensor_data,
            datapoint=datapoint,
            message=error_messages[datapoint],
            triggered_at=timestamp
        )

def main():
    def callback(ch, method, properties, body):
        try:
            data = json.loads(body)

            hotel_name = data['hotel_name']
            address = data['address']
            floor_number = data['floor']
            room_number = data.get('room_no')  # may be None
            datapoint = data['datapoint']
            value = data['value']
            timestamp = data['datetime']
            sensor_type = method.routing_key

            # Create or get Hotel, Floor, Room
            hotel, floor, room = get_or_create_location(hotel_name, address, floor_number, room_number)

            # Create or get Device
            device = get_or_create_device(hotel, room, sensor_type)

            # Save sensor reading
            sensor_data = save_sensor_data(device, datapoint, value, timestamp)

            # Check for fault
            check_fault(device, sensor_type, sensor_data, datapoint, value, timestamp)
        
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            print(f"Message content: {body}")

        data = json.loads(body)
        sensor_type = method.routing_key  # e.g., 'iaq', 'power_meter'
        
        if sensor_type == "iaq":
            print(f"IAQ Received {body}")
            # handle_iaq(data)
        elif sensor_type == "power":
            # handle_power(data)
            print(f"Power Meter Received {body}")
        elif sensor_type == "presence_sensor":
            print(f"Presence Sensor Received {body}")
        else:
            print(f"[!] Unknown routing key: {sensor_type}")

    # Establishing connection to RabbitMQ server
    # connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()

    # Declaring direct exchange
    channel.exchange_declare(exchange='sensor_exchange', exchange_type='direct')

    # Setting up queues
    channel.queue_declare(queue='iaq_sensor')
    channel.queue_bind(exchange='sensor_exchange', queue='iaq_sensor', routing_key='iaq')

    channel.queue_declare(queue='power_sensor')
    channel.queue_bind(exchange='sensor_exchange', queue='power_sensor', routing_key='power')

    # Set up consumers for queues
    channel.basic_consume(queue='iaq_sensor', on_message_callback=callback, auto_ack=True)
    channel.basic_consume(queue='power_sensor', on_message_callback=callback, auto_ack=True)

    # Start consuming
    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)