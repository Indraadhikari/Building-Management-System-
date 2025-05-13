import asyncio
import pynats
import random

async def generate_sensor_data():
    return {
        "temperature": random.uniform(20, 30),
        "humidity": random.uniform(30, 50),
        "energy_usage": random.uniform(100, 500)
    }

async def publish_data():
    client = pynats.Connection()
    await client.connect()
    while True:
        data = await generate_sensor_data()
        client.publish("sensor.data", str(data).encode())
        await asyncio.sleep(5)

asyncio.run(publish_data())