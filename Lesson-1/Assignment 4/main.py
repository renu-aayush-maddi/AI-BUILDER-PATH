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

print("KEY:", os.getenv("OPENAI_API_KEY"))
app = FastAPI(title="Acme SaaS Billing RAG Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai_client = OpenAI(api_key= os.getenv("OPENAI_API_KEY"))
if not openai_client:
    raise ValueError("OpenAI API key not found")

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = os.getenv("PINECONE_INDEX_NAME")
index = pc.Index(index_name)



class ChatRequest(BaseModel):
    query: str
    prompt_mode: str = "cot"   # "basic" | "refined" | "zot" (default: "cot")


#  Prompts 

BASIC_SYSTEM_PROMPT = """
You are a helpful assistant.
Answer the user's question about their billing issue.
Use the context provided below to answer accurately.
"""

REFINED_SYSTEM_PROMPT = """
You are a billing support specialist for Acme SaaS, a subscription-based
software platform offering Starter, Pro, and Enterprise plans.

Your role is to help customers resolve billing-related queries including:
- Subscription charges and plan changes
- Invoice discrepancies or incorrect charges
- Refund requests and eligibility
- Late fees and payment failures
- Cancellation and downgrade policies

Use ONLY the context retrieved from the Acme SaaS Billing Policy document
to answer. Do not invent policies or numbers not present in the context.

TONE: Professional, empathetic, and concise.

CONSTRAINTS:
- Never promise a refund or credit. Say:
  "I'll flag this for review by our billing team."
- If you cannot resolve the issue, escalate:
  "I'm raising a ticket for our billing team; expect a response within
   1 business day."
- Do not guess at internal account data you don't have access to.

OUTPUT FORMAT:
1. Acknowledge the issue in 1-2 sentences.
2. Explain the relevant policy or next step clearly (cite the policy).
3. State the action being taken (or ask for clarification if needed).
4. End with a reassuring closing line.
"""

COT_SYSTEM_PROMPT = """
You are a billing support specialist for Acme SaaS, a subscription-based
software platform offering Starter, Pro, and Enterprise plans.

A retrieval system has fetched the most relevant sections of the official
Acme SaaS Billing Policy document and placed them in the context below.
Base every answer strictly on that context - do not invent policies.

For EVERY billing query you must reason through the issue step-by-step
in a private <thinking> block before writing the customer-facing answer.

<thinking>
Step 1 – Classify: What type of billing problem is this?
         (duplicate charge / refund request / late fee / plan confusion /
          post-cancellation charge / payment failure / escalation needed / other)

Step 2 – Evidence: What does the retrieved policy context say about this
         exact situation? Quote the key rule or number.

Step 3 – Missing info: Do I have enough to fully resolve this, or do I
         need to ask the customer one clarifying question?

Step 4 – Action: Should I resolve directly, flag for billing team,
         request a waiver, or ask for clarification?

Step 5 – Draft: Write the final customer-facing response using the
         OUTPUT FORMAT below.
</thinking>

Then write only the FINAL RESPONSE — never show the <thinking> block.

OUTPUT FORMAT:
1. Acknowledge the issue (1-2 sentences).
2. Explain the relevant policy, citing specifics from the context.
3. State the action being taken.
4. Close with empathy.

TONE: Professional, empathetic, and concise.

CONSTRAINTS:
- Never promise a refund. Say: "I'll flag this for review by our billing team."
- Escalate when needed: "I'm raising a ticket for our billing team; expect
  a response within 1 business day."
- Do not guess at account data you don't have access to.
- If the policy context doesn't cover the question, say so clearly and escalate.
"""

PROMPTS = {
    "basic":    BASIC_SYSTEM_PROMPT,
    "refined":  REFINED_SYSTEM_PROMPT,
    "cot":      COT_SYSTEM_PROMPT,
}



def get_embedding(text: str) -> list[float]:
    try:
        response = openai_client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding Error: {str(e)}")


def chunk_text(text: str, size: int = 500, overlap: int = 100) -> list[str]:
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + size].strip())
        start += size - overlap
    return chunks


def build_user_prompt(context: str, query: str) -> str:
    return (
        "=== ACME SAAS BILLING POLICY CONTEXT (retrieved) ===\n"
        f"{context}\n"
        "=== END OF CONTEXT ===\n\n"
        f"Customer query: {query}"
    )


@app.post("/upload")
async def upload_and_ingest_pdf(file: UploadFile = File(...)):
    """Upload the billing policy PDF and store embeddings in Pinecone."""
    try:
        content = await file.read()
        pdf_reader = PdfReader(io.BytesIO(content))
        extracted_text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                extracted_text += page_text + "\n\n"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF read error: {str(e)}")

    chunks = chunk_text(extracted_text)

    vectors = []
    for chunk in chunks:
        embedding = get_embedding(chunk)
        vectors.append({
            "id": str(uuid.uuid4()),
            "values": embedding,
            "metadata": {"text": chunk, "source": file.filename},
        })

    try:
        index.upsert(vectors=vectors)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pinecone upsert error: {str(e)}")

    return {
        "message": f"Successfully processed '{file.filename}'.",
        "chunks_processed": len(vectors),
    }


@app.post("/chat")
async def chat(req: ChatRequest):
    """
    RAG-powered billing support chat.

    prompt_mode: "basic" | "refined" | "cot"  (default: "cot")
    """
    if req.prompt_mode not in PROMPTS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid prompt_mode. Choose from: {list(PROMPTS.keys())}",
        )

    # 1. Embed the customer query
    query_embedding = get_embedding(req.query)

    # 2. Retrieve top-k policy chunks from Pinecone
    try:
        search_results = index.query(
            vector=query_embedding,
            top_k=5,     
            include_metadata=True,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pinecone search error: {str(e)}")

    contexts = [m["metadata"]["text"] for m in search_results["matches"]]
    context_text = "\n---\n".join(contexts)

    # 3. Select the appropriate system prompt
    system_prompt = PROMPTS[req.prompt_mode]

    # 4. Build the user message with injected context
    user_prompt = build_user_prompt(context_text, req.query)

    # 5. Call the LLM
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=0.3,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI chat error: {str(e)}")

    sources = list({m["metadata"].get("source", "Unknown") for m in search_results["matches"]})

    return {
        "answer":           response.choices[0].message.content,
        "prompt_mode":      req.prompt_mode,
        "sources":          sources,
        "context_snippets": contexts,
    }


TEST_CASES = [
    "I was charged twice this month.",
    "Why did I get a late fee when auto-pay is enabled?",
    "I cancelled my subscription but still got billed.",
    "Your company scammed me.",
    "Can I get a refund for last month's payment?",
]


@app.get("/run-tests")
async def run_tests():
    """
    Run all test cases through all three prompt modes and return a
    side-by-side comparison. Results are also saved to results.json.
    """
    import json

    results = []
    for case in TEST_CASES:
        case_result = {"user_input": case}
        for mode in PROMPTS:
            req = ChatRequest(query=case, prompt_mode=mode)
            resp = await chat(req)
            case_result[mode] = resp["answer"]
        results.append(case_result)

    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    return results
