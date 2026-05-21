import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore


load_dotenv()

mcp = FastMCP("rag-server")

INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
EMBEDDING_MODEL = "text-embedding-3-small"
TOP_K = 5


def load_vectorstore():

    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    return PineconeVectorStore(index_name=INDEX_NAME,embedding=embeddings)


@mcp.tool()
def search_hr_policy(query: str) -> str:

    try:

        vectorstore = load_vectorstore()

        results = vectorstore.similarity_search(query,k=TOP_K)

        if not results:
            return "No HR policy results found."

        formatted = []

        for i, doc in enumerate(results, 1):

            source = doc.metadata.get("source","HR Policy")
            formatted.append(f"[{i}] Source: {source}\n{doc.page_content}")

        return "\n\n".join(formatted)

    except Exception as e:

        return f"RAG Error: {e}"


if __name__ == "__main__":

    mcp.run()