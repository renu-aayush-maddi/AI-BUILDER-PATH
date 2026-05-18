"""
mcp_server/google_docs_server.py
─────────────────────────────────
MCP Server that exposes a Google Docs reader as a tool.
Runs as an HTTP server using the `mcp` SDK.

Start with:
    python mcp_server/google_docs_server.py
"""

import os
import json
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Google API imports
from googleapiclient.discovery import build
from google.oauth2 import service_account

load_dotenv()

# ── Configuration ─────────────────────────────────────────────────────────────
CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
DEFAULT_DOC_ID = os.getenv("GOOGLE_DOC_ID", "")
SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]

# ── MCP Server Init ───────────────────────────────────────────────────────────
mcp = FastMCP(
    name="presidio-google-docs"
)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _get_docs_service():
    """Build and return an authenticated Google Docs service client."""
    if not os.path.exists(CREDENTIALS_PATH):
        raise FileNotFoundError(
            f"Google credentials not found at '{CREDENTIALS_PATH}'. "
            "Set GOOGLE_CREDENTIALS_PATH in your .env file."
        )
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH, scopes=SCOPES
    )
    return build("docs", "v1", credentials=creds)


def _extract_text_from_doc(document: dict) -> str:
    """Recursively extract plain text from a Google Docs document body."""
    text_parts: list[str] = []
    body = document.get("body", {})
    for element in body.get("content", []):
        paragraph = element.get("paragraph")
        if not paragraph:
            continue
        for part in paragraph.get("elements", []):
            text_run = part.get("textRun")
            if text_run:
                text_parts.append(text_run.get("content", ""))
    return "".join(text_parts)


# ── MCP Tools ─────────────────────────────────────────────────────────────────
@mcp.tool()
def read_google_doc(doc_id: str = "") -> str:
    """
    Read the full text content of a Google Doc.

    Args:
        doc_id: The Google Document ID (found in its URL). 
                Defaults to the GOOGLE_DOC_ID env variable.

    Returns:
        The plain-text content of the document.
    """
    target_doc_id = doc_id or DEFAULT_DOC_ID
    if not target_doc_id:
        return "Error: No Google Doc ID provided. Set GOOGLE_DOC_ID in .env or pass doc_id."

    try:
        service = _get_docs_service()
        document = service.documents().get(documentId=target_doc_id).execute()
        title = document.get("title", "Untitled")
        content = _extract_text_from_doc(document)
        return f"# {title}\n\n{content}"
    except Exception as e:
        return f"Error reading Google Doc '{target_doc_id}': {e}"


@mcp.tool()
def search_google_doc(query: str, doc_id: str = "") -> str:
    """
    Search for a specific query within a Google Doc and return relevant excerpts.

    Args:
        query:  The search term or question to look for.
        doc_id: The Google Document ID. Defaults to GOOGLE_DOC_ID env variable.

    Returns:
        Relevant paragraphs from the document that contain the query term.
    """
    target_doc_id = doc_id or DEFAULT_DOC_ID
    if not target_doc_id:
        return "Error: No Google Doc ID provided."

    try:
        service = _get_docs_service()
        document = service.documents().get(documentId=target_doc_id).execute()
        full_text = _extract_text_from_doc(document)

        # Simple keyword search — return matching paragraphs
        query_lower = query.lower()
        paragraphs = [p.strip() for p in full_text.split("\n") if p.strip()]
        matches = [p for p in paragraphs if query_lower in p.lower()]

        if not matches:
            return f"No content found in the document matching: '{query}'"

        result = f"Found {len(matches)} relevant section(s) for '{query}':\n\n"
        result += "\n\n---\n\n".join(matches[:10])  # limit to 10 matches
        return result
    except Exception as e:
        return f"Error searching Google Doc: {e}"


@mcp.tool()
def list_available_docs() -> str:
    """
    List the configured Google Doc(s) this MCP server can access.

    Returns:
        JSON with available document IDs and their titles.
    """
    if not DEFAULT_DOC_ID:
        return json.dumps({"docs": [], "note": "No GOOGLE_DOC_ID configured."})

    try:
        service = _get_docs_service()
        document = service.documents().get(documentId=DEFAULT_DOC_ID).execute()
        return json.dumps({
            "docs": [
                {
                    "id": DEFAULT_DOC_ID,
                    "title": document.get("title", "Untitled"),
                }
            ]
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 Presidio Google Docs MCP Server starting on http://localhost:8000 ...")
    mcp.run(transport="sse")