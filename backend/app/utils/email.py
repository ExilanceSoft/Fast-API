# banjos_restaurant\app\utils\email.py
from jinja2 import Environment, FileSystemLoader
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

env = Environment(loader=FileSystemLoader('app/templates/emails'))

def send_email(recipient: str, subject: str, template_name: str, context: dict = None) -> None:
    """Send email using a template with given context"""
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")

    if not sender or not password:
        print("Error: Email sender or password missing")
        return

    # Render the template
    template = env.get_template(template_name)
    body = template.render(**(context or {}))

    # Create message
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
        print(f"Email sent to {recipient}")
    except Exception as e:
        print(f"Error sending email: {e}")