from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent import build_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = build_agent()


class QueryRequest(BaseModel):
    query: str


@app.post("/chat")
async def chat(req: QueryRequest):

    try:

        response = agent.invoke({
            "input": req.query
        })

        return {
            "success": True,
            "response": response["output"]
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }