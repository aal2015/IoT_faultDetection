import pika
import json
import csv
import time
import threading
import django
import os
import sys

# Add the path to the BASE DIR
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Set the settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

# Setup Django
django.setup()

# Getting sensor data directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SENSOR_DATA_DIR = os.path.join(BASE_DIR, 'faultDetection', 'agents', 'sensor_data')

hotel_name = "Novotel"
address = "Khlong Nueng, Khlong Luang District, Pathum Thani"
floor = 1

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

def publish_sensor_data(file_path, routing_key, room_no=None):
    connection = connect_to_rabbitmq()
    channel = connection.channel()

    # Declare exchange and routing key
    channel.exchange_declare(exchange='sensor_exchange', exchange_type='direct')

    queue_name = f'{routing_key}_sensor'
    channel.queue_declare(queue=queue_name)
    channel.queue_bind(exchange='sensor_exchange', queue=queue_name, routing_key=routing_key)

    # Read the CSV file
    try:
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                for key in row:
                    if key == 'datetime':
                        continue
                    
                    message = {
                        'datetime': row['datetime'],
                        'room_no': room_no if routing_key in ['iaq', 'presence_sensor'] else None,
                        'floor': floor if routing_key in ['iaq', 'presence_sensor'] else None,
                        'datapoint': key,
                        'value': row[key],
                        'hotel_name': hotel_name,
                        'address': address
                    }

                    # Publish to RabbitMQ
                    channel.basic_publish(
                        exchange='sensor_exchange',
                        routing_key=routing_key,
                        body=json.dumps(message)
                    )
                    print(f"[{key}] Sent: {message}")
                time.sleep(5)
    except Exception as e:
        print(f"❌ Error reading/publishing file {file_path}: {e}")
    finally:
        connection.close()

# Sensor config
sensors = [
    (os.path.join(SENSOR_DATA_DIR, "sample_iaq_data_Room101.csv"), "iaq", "101"),
    (os.path.join(SENSOR_DATA_DIR, "sample_iaq_data_Room102.csv"), "iaq", "102"),
    (os.path.join(SENSOR_DATA_DIR, "sample_iaq_data_Room103.csv"), "iaq", "103"),
    (os.path.join(SENSOR_DATA_DIR, "sample_power_meter_data.csv"), "power", None),
]

# Launch threads
threads = []
for file_path, routing_key, room_no in sensors:
    t = threading.Thread(target=publish_sensor_data, args=(file_path, routing_key, room_no))
    t.start()
    threads.append(t)

# Wait for all threads to complete (keeps container running)
for t in threads:
    t.join()
