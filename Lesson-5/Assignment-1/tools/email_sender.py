# def send_support_email(
#     ticket_id,
#     question,
#     department
# ):

#     print(
#         f"""
#         EMAIL SENT

#         Ticket: {ticket_id}

#         Department: {department}

#         Question:
#         {question}
#         """
#     )


import os
import smtplib

from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()


def send_support_email(
    ticket_id: str,
    question: str,
    department: str
):

    sender = os.getenv("EMAIL_FROM")
    receiver = os.getenv("EMAIL_TO")
    password = os.getenv("EMAIL_PASSWORD")

    subject = f"Support Ticket Raised - {ticket_id}"

    body = f"""
A new support ticket requires manual attention.

Ticket ID:
{ticket_id}

Department:
{department}

User Question:
{question}
"""

    message = MIMEText(body)

    message["Subject"] = subject
    message["From"] = sender
    message["To"] = receiver

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

        print("EMAIL SENT")

    except Exception as ex:

        print(
            f"EMAIL FAILED: {ex}"
        )