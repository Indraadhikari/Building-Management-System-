import asyncio
import json
import random
from datetime import datetime
from nats.aio.client import Client as NATS

async def simulate_sensor():
    nc = NATS()
    await nc.connect("nats://nats:4222")  #nats service name from Docker Compose

    while True:
        data = {
            "sensor_id": "sensor-101",
            "temperature": round(random.uniform(20.0, 25.0), 2),
            "humidity": round(random.uniform(40.0, 60.0), 2),
            "energy_kwh": round(random.uniform(0.5, 2.0), 2),
            "timestamp": datetime.utcnow().isoformat()
        }

        await nc.publish("building.sensor.data", json.dumps(data).encode())
        print("Published:", data)
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(simulate_sensor())
