import bme680
import paho.mqtt.client as mqtt
import json
import time

# debugging
skip_bme = True

# Define the MQTT settings
MQTT_BROKER = "192.168.0.223"
MQTT_PORT = 1883
MQTT_USERNAME = "mqttuser"
MQTT_PASSWORD = "mqttpass"
MQTT_DISCOVERY_TOPIC = "homeassistant/sensor/bedroom_temperature/config"
MQTT_STATE_TOPIC_TEMP = "home/bedroom/temperature"
MQTT_STATE_TOPIC_HUM = "home/bedroom/humidity"
MQTT_STATE_TOPIC_AIR = "home/bedroom/air_quality"
MQTT_STATE_TOPIC_PRESS = "home/bedroom/pressure"

device_config = {
    "name": "Bedroom Sensor",
    "identifiers": ["bedroom_sensor_1"],
    "manufacturer": "DumDevices",
    "model": "BME680",
    "sw_version": "1.0"
}

sensor_configs = [
    {
        "name": "Bedroom Temperature",
        "state_topic": MQTT_STATE_TOPIC_TEMP,
        "unit_of_measurement": "°C",
        "device_class": "temperature",
        "value_template": "{{ value }}",
        "unique_id": "bedroom_temperature_sensor_1",
        "device": device_config
    },
    {
        "name": "Bedroom Humidity",
        "state_topic": MQTT_STATE_TOPIC_HUM,
        "unit_of_measurement": "%",
        "device_class": "humidity",
        "value_template": "{{ value }}",
        "unique_id": "bedroom_humidity_sensor_1",
        "device": device_config
    },
    {
        "name": "Bedroom Air Quality",
        "state_topic": MQTT_STATE_TOPIC_AIR,
        "unit_of_measurement": "Ohms",
        "value_template": "{{ value }}",
        "unique_id": "bedroom_air_quality_sensor_1",
        "device": device_config
    },
    {
        "name": "Bedroom Pressure",
        "state_topic": MQTT_STATE_TOPIC_PRESS,
        "unit_of_measurement": "hPa",
        "device_class": "pressure",
        "value_template": "{{ value }}",
        "unique_id": "bedroom_pressure_sensor_1",
        "device": device_config
    }
]

# Define the callback functions
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connected successfully")
        for config in sensor_configs:
            client.publish(f"homeassistant/sensor/{config['unique_id']}/config", json.dumps(config), retain=True)
    else:
        print(f"Failed to connect, reason code: {reason_code}")

def on_message(client, userdata, msg):
    print(f"{msg.topic} {msg.payload}")

def perform_measurement():
    if skip_bme:
        return {
            'temperature': 15,
            'pressure': 1000,
            'humidity': 20,
            'air_quality': 100,
        }
    elif sensor.get_sensor_data() and sensor.data.heat_stable:
        return {
            'temperature': sensor.data.temperature,
            'humidity': sensor.data.humidity,
            'air_quality': sensor.data.gas_resistance,
            'pressure': sensor.data.pressure,
        }

if not skip_bme:
    sensor = bme680.BME680()
    sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
    sensor.set_gas_heater_temperature(320)
    sensor.set_gas_heater_duration(150)
    sensor.select_gas_heater_profile(0)
    sensor.set_filter(bme680.FILTER_SIZE_3)

# Create an MQTT client instance with the specified callback API version
client = mqtt.Client(protocol=mqtt.MQTTv5, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

while True:
    mes = perform_measurement()
    client.publish(MQTT_STATE_TOPIC_TEMP, str(mes['temperature']))
    client.publish(MQTT_STATE_TOPIC_HUM, str(mes['humidity']))
    client.publish(MQTT_STATE_TOPIC_AIR, str(mes['air_quality']))
    client.publish(MQTT_STATE_TOPIC_PRESS, str(mes['pressure']))
    time.sleep(5)  # Publish every 60 seconds