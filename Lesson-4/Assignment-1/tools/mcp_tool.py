import os
import re
from dotenv import load_dotenv
from langchain_core.tools import Tool

from googleapiclient.discovery import build
from google.oauth2 import service_account

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]

creds = service_account.Credentials.from_service_account_file(
    os.getenv("GOOGLE_CREDENTIALS_PATH"),
    scopes=SCOPES
)

service = build("docs", "v1", credentials=creds)

DOC_ID = os.getenv("GOOGLE_DOC_ID")


def query_google_docs(query: str) -> str:

    document = service.documents().get(
        documentId=DOC_ID
    ).execute()

    content = ""

    for element in document.get("body").get("content"):

        paragraph = element.get("paragraph")

        if paragraph:

            for elem in paragraph.get("elements"):

                text_run = elem.get("textRun")

                if text_run:
                    content += text_run.get("content")

    
    query_words = re.findall(r"\w+", query.lower())
    matches = []

    for line in content.split("\n"):

        line_lower = line.lower()

        score = sum(
            1 for word in query_words
            if word in line_lower
        )

        if score >= 2:
            matches.append(line)

    if not matches:
        return content[:3000]

    return "\n".join(matches[:20])


def get_mcp_tool():

    return Tool(
        name="google_docs_mcp",
        func=query_google_docs,
        description=(
            "Search Google Docs for internal Presidio company information, "
            "customer feedback, insurance operations, and marketing reports."
        ),
    )