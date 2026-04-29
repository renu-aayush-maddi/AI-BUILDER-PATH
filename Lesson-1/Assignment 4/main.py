import os
import uuid
import io
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from openai import OpenAI
from pinecone import Pinecone
from dotenv import load_dotenv
from pypdf import PdfReader 
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(title="RAG Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY").strip()
)
print("API KEY:", os.getenv("OPENAI_API_KEY"))

if not openai_client:
    raise ValueError("API key not found")

# Pinecone 
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = os.getenv("PINECONE_INDEX_NAME")
index = pc.Index(index_name)


class ChatRequest(BaseModel):
    query: str

# Helper Function
def get_embedding(text: str) -> list[float]:
    try:
        response = openai_client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Embedding Error:{str(e)}")
    
def chunk_text(text, size=500, overlap=100):
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start += size - overlap
    
    return chunks

# Endpoints

@app.post("/upload")
async def upload_and_ingest_pdf(file: UploadFile = File(...)):
    try:
        content = await file.read()
        pdf_reader = PdfReader(io.BytesIO(content))
        
        extracted_text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                extracted_text += page_text + "\n\n"
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading PDF: {str(e)}")

    # Chunking
    chunks = chunk_text(extracted_text)

    # Embed and Upsert
    vectors = []
    for chunk in chunks:
        embedding = get_embedding(chunk)
        vector_id = str(uuid.uuid4())
        vectors.append({
            "id": vector_id,
            "values": embedding,
            "metadata": {
                "text": chunk,
                "source": file.filename 
            }
        })
        
    try:
        index.upsert(vectors=vectors)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pinecone Upsert Error: {str(e)}")
        
    return {
        "message": f"Successfully processed '{file.filename}'.",
        "chunks_processed": len(vectors)
    }

@app.post("/chat")
async def chat(req: ChatRequest):
    query_embedding = get_embedding(req.query)
    
    try:
        search_results = index.query(
            vector=query_embedding,
            top_k=3,
            include_metadata=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pinecone Search Error: {str(e)}")
    
    contexts = [match['metadata']['text'] for match in search_results['matches']]
    context_text = "\n---\n".join(contexts)
    
    system_prompt = (
        "You are a highly capable AI assistant. Answer the user's question "
        "using ONLY the provided context. If the context does not contain "
        "the answer, state 'I cannot answer this based on the provided context.'"
    )
    
    user_prompt = f"Context Information:\n{context_text}\n\nUser Question: {req.query}"
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI Chat Error: {str(e)}")

    sources = list(set([match['metadata'].get('source', 'Unknown') for match in search_results['matches']]))
    
    return {
        "answer": response.choices[0].message.content,
        "sources": sources,
        "context_snippets": contexts
    }