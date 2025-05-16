import asyncio, os
import json
from datetime import datetime
from nats.aio.client import Client as NATS
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# InfluxDB 
INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
ORG = os.getenv("ORG")
BUCKET = os.getenv("BUCKET")

async def main():
    # Connect to NATS
    nc = NATS()
    print(f"Attempting to connect to NAT")
    await nc.connect("nats://nats:4222", connect_timeout=10)  #nats service name
    print("Successfully connected to NATS.")

    # Connect to InfluxDB
    influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
    write_api = influx_client.write_api(write_options=SYNCHRONOUS)

    # Callback on message received
    async def handler(msg):
        try:
            data = json.loads(msg.data.decode())
            now = datetime.utcnow()

            # Save raw data
            # Masurement "raw_data"
            point = Point("raw_data") \
                .tag("sensor_id", data["sensor_id"]) \
                .field("temperature", data["temperature"]) \
                .field("humidity", data["humidity"]) \
                .field("energy_kwh", data["energy_kwh"]) \
                .time(now)

            write_api.write(bucket=BUCKET, org=ORG, record=point)

            # aggregation

            temp_F = (data["temperature"] * 9/5) + 32  
            # only for example we can implement advance data agreegation logic likewise.
            # Masurement "aggregated_data"
            agg_point = Point("aggregated_data") \
                .tag("sensor_id", data["sensor_id"]) \
                .field("temperature_f", temp_F) \
                .time(now)

            write_api.write(bucket=BUCKET, org=ORG, record=agg_point)

            print(f"Stored raw & aggregated data for {data['sensor_id']}")

        except Exception as e:
            print(f"Error processing message: {e}")

    await nc.subscribe("building.sensor.data", cb=handler)

    print("Listening for incoming sensor data...")
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())