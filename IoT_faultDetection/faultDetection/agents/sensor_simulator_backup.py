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
address = " Khlong Nueng, Khlong Luang District, Pathum Thani"
floor = 1

def publish_sensor_data(file_path, routing_key, room_no=None):
    # 1. Connect to RabbitMQ
    # connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()

    # 2. Declare exchange and routing key
    channel.exchange_declare(exchange='sensor_exchange', exchange_type='direct')

    channel.queue_declare(queue=f'{routing_key}_sensor')
    channel.queue_bind(exchange='sensor_exchange', queue=f'{routing_key}_sensor', routing_key=routing_key)

    # 3. Open and read the CSV file
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Add fields dynamically
            for key in row:
                if key == 'datetime':
                    continue
                
                message = {
                    'datetime': row['datetime']
                }

                if routing_key in ['iaq', 'presence_sensor']:
                    message["room_no"] = room_no
                    message["floor"] = floor
                else:
                    message["room_no"] = None
                    message["floor"] = None
                    
                message['datapoint'] = key
                message['value'] = row[key]
                message["hotel_name"] = hotel_name
                message["address"] = address
                

                # 4. Publish the message to RabbitMQ
                channel.basic_publish(
                    exchange='sensor_exchange',
                    routing_key=routing_key,
                    body=json.dumps(message)
                )
                print(f"[{key}] Sent: {message}")
            time.sleep(5)

    connection.close()

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