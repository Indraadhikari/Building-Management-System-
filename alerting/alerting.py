import asyncio, os, json, smtplib
from email.mime.text import MIMEText
from nats.aio.client import Client as NATS

TEMP_THRESHOLD = float(os.getenv("ALERT_THRESHOLD_TEMP"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_RECIPIENT = os.getenv("ALERT_RECIPIENT")

async def send_alert(sensor_id, temp):
    msg = MIMEText(f" Temperature too high! Sensor {sensor_id} reported {temp}°C. \n This is the test arlerting notification from the developement environment by Indra for Piscada.")
    msg['Subject'] = '🔥 High Temperature Alert - Piscada (Indra)'
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_RECIPIENT
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
            print(f"Alert sent for {sensor_id}")
    except Exception as e:
        print(f"Alert send failed: {e}")

async def main():
    nc = NATS()
    await nc.connect("nats://nats:4222")

    async def handler(msg):
        try:
            data = json.loads(msg.data.decode())
            sensor_id = data["sensor_id"]
            temp = data["temperature"]
            if temp > TEMP_THRESHOLD:
                await send_alert(sensor_id, temp)
        except Exception as e:
            print(f"Error in alerting: {e}")

    await nc.subscribe("building.sensor.data", cb=handler) # subscribe subject building.sensor.data
    print("Alerting service is running...")
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
