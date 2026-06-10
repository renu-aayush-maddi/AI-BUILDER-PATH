import os
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv

load_dotenv()


def send_ticket_email(
    ticket_id: str,
    department: str,
    user_query: str,
    response: str
):

    sender = os.getenv("EMAIL_FROM")
    receiver = os.getenv("EMAIL_TO")
    password = os.getenv("EMAIL_PASSWORD")

    subject = f"New Support Ticket - {ticket_id}"

    body = f"""
New Support Ticket Created

Ticket ID:
{ticket_id}

Department:
{department}

User Query:
{user_query}

Response:
{response}
"""

    message = MIMEMultipart()

    message["From"] = sender
    message["To"] = receiver
    message["Subject"] = subject

    message.attach(
        MIMEText(body, "plain")
    )

    try:

        with smtplib.SMTP(
            "smtp.gmail.com",
            587
        ) as server:

            server.starttls()

            server.login(
                sender,
                password
            )

            server.send_message(message)

        print("Email sent successfully")

    except Exception as e:

        print(
            f"Email sending failed: {e}"
        )