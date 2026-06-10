from tools.email_sender import send_support_email
import os
from dotenv import load_dotenv  

load_dotenv()

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

print("EMAIL_FROM:", EMAIL_FROM)
print("EMAIL_PASSWORD:", EMAIL_PASSWORD)

send_support_email(
    ticket_id="123",
    question="VPN is not working",
    department="IT"
)
