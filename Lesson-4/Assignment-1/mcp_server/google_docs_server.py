import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from googleapiclient.discovery import build
from google.oauth2 import service_account

load_dotenv()

CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH","credentials.json")

DEFAULT_DOC_ID = os.getenv("GOOGLE_DOC_ID","")

SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]

mcp = FastMCP( name="presidio-google-docs")


def get_service():

    creds = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH,scopes=SCOPES)
    return build("docs","v1",credentials=creds)


@mcp.tool()
def search_google_doc(query: str,doc_id: str = ""):

    service = get_service()

    document = service.documents().get(documentId=doc_id or DEFAULT_DOC_ID).execute()

    text = ""

    for element in document["body"]["content"]:

        paragraph = element.get("paragraph")

        if not paragraph:
            continue

        for part in paragraph.get("elements", []):

            text_run = part.get("textRun")

            if text_run:
                text += text_run.get(
                    "content",
                    ""
                )

    matches = []

    query_words = query.lower().split()

    for line in text.split("\n"):

        score = sum(
            1 for word in query_words
            if word in line.lower()
        )

        if score > 0:
            matches.append(line)

    return "\n".join(matches[:10])


if __name__ == "__main__":
    mcp.run(transport="sse")