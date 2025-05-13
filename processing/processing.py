import pynats
from influxdb_client import InfluxDBClient

def process_data(message):
    client = InfluxDBClient(url="http://localhost:8086", token="my-token", org="my-org")
    write_api = client.write_api()
    # Format and write the message data to InfluxDB
    write_api.write("sensor_bucket", "my-org", message.data.decode())
    # Add additional aggregation logic here

client = pynats.Connection()
client.connect()
client.subscribe("sensor.data", process_data)