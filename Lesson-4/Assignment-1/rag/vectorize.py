"""
rag/vectorize.py
─────────────────
Reads all .txt and .pdf files from the data/ directory,
splits them into chunks, and upserts embeddings into Pinecone.

Run once (and re-run whenever documents change):
    uv run python rag/vectorize.py
"""

import os
import glob
import time
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "presidio-hr-policies")
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMS = 1536   # dimensions for text-embedding-3-small
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


# ── Helpers ───────────────────────────────────────────────────────────────────
def _get_pinecone_client() -> Pinecone:
    if not PINECONE_API_KEY:
        raise EnvironmentError(
            "PINECONE_API_KEY is not set. Add it to your .env file."
        )
    return Pinecone(api_key=PINECONE_API_KEY)


def _ensure_index(pc: Pinecone) -> None:
    """Create the Pinecone index if it doesn't already exist."""
    existing = [idx.name for idx in pc.list_indexes()]
    if INDEX_NAME in existing:
        print(f"  ✅ Pinecone index '{INDEX_NAME}' already exists.")
        return

    print(f"  🛠️  Creating Pinecone index '{INDEX_NAME}' ...")
    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBEDDING_DIMS,
        metric="cosine",
        spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION),
    )

    # Wait until the index is ready
    print("  ⏳ Waiting for index to become ready ...", end="", flush=True)
    while not pc.describe_index(INDEX_NAME).status["ready"]:
        print(".", end="", flush=True)
        time.sleep(2)
    print(" ready!")


def load_documents(data_dir: str):
    """Load all .txt and .pdf files from the data directory."""
    documents = []

    for path in glob.glob(os.path.join(data_dir, "**/*.txt"), recursive=True):
        print(f"  📄 Loading TXT: {path}")
        loader = TextLoader(path, encoding="utf-8")
        documents.extend(loader.load())

    for path in glob.glob(os.path.join(data_dir, "**/*.pdf"), recursive=True):
        print(f"  📄 Loading PDF: {path}")
        loader = PyPDFLoader(path)
        documents.extend(loader.load())

    return documents


# ── Main ──────────────────────────────────────────────────────────────────────
def vectorize():
    print("🔍 Loading documents from data/ ...")
    docs = load_documents(DATA_DIR)

    if not docs:
        print("⚠️  No documents found in data/. Add .txt or .pdf files and rerun.")
        return

    print(f"✅ Loaded {len(docs)} document(s).")

    print("✂️  Splitting into chunks ...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    print(f"✅ Created {len(chunks)} chunks.")

    print("🌲 Connecting to Pinecone ...")
    pc = _get_pinecone_client()
    _ensure_index(pc)

    print("🧠 Generating embeddings and upserting to Pinecone ...")
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        index_name=INDEX_NAME,
    )

    # Confirm count
    index = pc.Index(INDEX_NAME)
    stats = index.describe_index_stats()
    total = stats.get("total_vector_count", "unknown")
    print(f"✅ Pinecone index '{INDEX_NAME}' now holds {total} vectors.")
    print("🎉 Vectorization complete! You can now run: uv run python agent.py")


if __name__ == "__main__":
    vectorize()