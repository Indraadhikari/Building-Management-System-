import asyncio
import json
import random
from datetime import datetime
from nats.aio.client import Client as NATS

async def simulate_sensor():
    nc = NATS()
    print(f"Attempting to connect to NAT")
    await nc.connect("nats://nats:4222", connect_timeout=10)  #nats service name from Docker Compose
    print("Successfully connected to NATS.")

    sensor_ids = ["sensor-101", "sensor-102", "sensor-103", "sensor-104"]

    while True:
        data = {
            "sensor_id": random.choice(sensor_ids),
            "temperature": round(random.uniform(20.0, 25.0), 2),
            "humidity": round(random.uniform(40.0, 60.0), 2),
            "energy_kwh": round(random.uniform(0.5, 2.0), 2),
            "timestamp": datetime.utcnow().isoformat()
        }

        await nc.publish("building.sensor.data", json.dumps(data).encode()) #subject building.sensor.data
        print("Published:", data)
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(simulate_sensor())