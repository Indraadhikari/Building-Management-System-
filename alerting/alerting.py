import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_alert(subject, body, from_email, to_email, smtp_server="smtp.gmail.com", smtp_port=587, username=None, password=None):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            server.sendmail(from_email, to_email, msg.as_string())
            print(f"✅ Alert sent to {to_email}")
    except smtplib.SMTPException as e:
        print(f"❌ Error sending alert: {e}")

# Example usage
send_alert(
    subject="Temperature Alert",
    body="Temperature exceeded threshold.",
    from_email="indrabdradhikari39@gmail.com",
    to_email="indraadhikari0@gmail.com",
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    username="indrabdradhikari39@gmail.com",
    password="XXXXXXXXXXXXXXX"
)
