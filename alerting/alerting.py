import pynats
from smtplib import SMTP

def check_for_alerts(message):
    data = eval(message.data.decode())
    if data['temperature'] > 28:  # Example threshold condition
        send_alert("Temperature Alert", "Temperature exceeded threshold.")

def send_alert(subject, body):
    with SMTP('localhost') as smtp:
        smtp.sendmail('indrabdradhikari39@gmail.com', 'indraadhikari0@gmail.com', f"Subject: {subject}\n\n{body}")

client = pynats.Connection()
client.connect()
client.subscribe("sensor.data", check_for_alerts)