import asyncio, os
import json
from datetime import datetime
from nats.aio.client import Client as NATS
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# InfluxDB settings
INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
ORG = os.getenv("ORG")
BUCKET = os.getenv("BUCKET")

async def main():
    # Connect to NATS
    nc = NATS()
    await nc.connect("nats://nats:4222")  # Use service name from docker-compose

    # Connect to InfluxDB
    influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
    write_api = influx_client.write_api(write_options=SYNCHRONOUS)

    # Callback on message received
    async def handler(msg):
        try:
            data = json.loads(msg.data.decode())
            now = datetime.utcnow()

            # Save raw data
            point = Point("raw_data") \
                .tag("sensor_id", data["sensor_id"]) \
                .field("temperature", data["temperature"]) \
                .field("humidity", data["humidity"]) \
                .field("energy_kwh", data["energy_kwh"]) \
                .time(now)

            write_api.write(bucket=BUCKET, org=ORG, record=point)

            # Optionally compute aggregation (simple average simulation here)
            avg_temp = data["temperature"]  # Placeholder — use real logic in prod
            agg_point = Point("aggregated_data") \
                .tag("sensor_id", data["sensor_id"]) \
                .field("avg_temperature", avg_temp) \
                .time(now)

            write_api.write(bucket=BUCKET, org=ORG, record=agg_point)

            print(f"✅ Stored raw & aggregated data for {data['sensor_id']}")

        except Exception as e:
            print(f"❌ Error processing message: {e}")

    await nc.subscribe("building.sensor.data", cb=handler)

    print("🔄 Listening for incoming sensor data...")
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())