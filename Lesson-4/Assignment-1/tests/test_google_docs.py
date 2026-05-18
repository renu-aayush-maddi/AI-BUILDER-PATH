from googleapiclient.discovery import build
from google.oauth2 import service_account
from dotenv import load_dotenv
import os

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]

creds = service_account.Credentials.from_service_account_file(
    os.getenv("GOOGLE_CREDENTIALS_PATH"),
    scopes=SCOPES
)

service = build("docs", "v1", credentials=creds)

doc_id = os.getenv("GOOGLE_DOC_ID")

document = service.documents().get(documentId=doc_id).execute()

print("\n✅ GOOGLE DOC TITLE:\n")
print(document.get("title"))