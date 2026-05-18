"""
rag/rag_tool.py
────────────────
LangChain Tool wrapper around Pinecone vectorstore.
Used by the agent to answer questions from HR policy documents.
"""

import os
from dotenv import load_dotenv

from langchain_core.tools import Tool
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

load_dotenv()

INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "presidio-hr-policies")
EMBEDDING_MODEL = "text-embedding-3-small"
TOP_K = 5


def _load_vectorstore() -> PineconeVectorStore:
    """Connect to the existing Pinecone index."""
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    return PineconeVectorStore(
        index_name=INDEX_NAME,
        embedding=embeddings,
    )


def search_hr_policy(query: str) -> str:
    """
    Search the Presidio HR Policy Pinecone index for relevant information.

    Args:
        query: A natural language question about HR policies.

    Returns:
        Relevant excerpts from HR policy documents.
    """
    try:
        vectorstore = _load_vectorstore()
        results = vectorstore.similarity_search(query, k=TOP_K)

        if not results:
            return f"No relevant HR policy content found for: '{query}'"

        formatted = []
        for i, doc in enumerate(results, 1):
            source = doc.metadata.get("source", "HR Policy Document")
            formatted.append(f"**[Excerpt {i}]** (Source: {source})\n{doc.page_content}")

        return "\n\n---\n\n".join(formatted)

    except Exception as e:
        return (
            f"❌ Error querying Pinecone RAG tool: {e}\n"
            "Make sure you've run `uv run python rag/vectorize.py` first "
            "and that PINECONE_API_KEY is set in your .env file."
        )


def get_rag_tool() -> Tool:
    """Return a configured LangChain Tool for HR Policy RAG retrieval via Pinecone."""
    return Tool(
        name="hr_policy_search",
        func=search_hr_policy,
        description=(
            "Use this tool to answer questions about Presidio's internal HR policies, "
            "including leave policies, parental leave, performance reviews, hiring, "
            "benefits, compensation, remote work, data privacy, AI usage guidelines, "
            "compliance, and workplace conduct. "
            "Input should be a specific question or search query."
        ),
    )