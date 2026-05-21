import os
import re

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from googleapiclient.discovery import build
from google.oauth2 import service_account


load_dotenv()

mcp = FastMCP("google-docs-server")

SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]

CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")
DOC_ID = os.getenv("GOOGLE_DOC_ID")

def get_service():

    creds = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH,scopes=SCOPES)
    return build("docs","v1",credentials=creds)


@mcp.tool()
def search_google_docs(query: str) -> str:

    service = get_service()

    document = service.documents().get(documentId=DOC_ID).execute()

    content = ""

    for element in document["body"]["content"]:

        paragraph = element.get("paragraph")

        if not paragraph:
            continue

        for elem in paragraph.get("elements", []):

            text_run = elem.get("textRun")

            if text_run:
                content += text_run.get("content","")

    query_words = re.findall(r"\w+",query.lower())

    matches = []

    for line in content.split("\n"):

        line_lower = line.lower()

        score = sum(
            1
            for word in query_words
            if word in line_lower
        )

        if score >= 2:
            matches.append(line)

    if not matches:
        return content[:3000]

    return "\n".join(matches[:20])


if __name__ == "__main__":

    mcp.run()