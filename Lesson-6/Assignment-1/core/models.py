# STRUCTURED OUTPUTS

from typing import List
from pydantic import BaseModel, Field


class SupervisorDecision(BaseModel):
    departments: List[str]
    reasoning: str


class AgentResponse(BaseModel):
    answer: str
    confidence: float = Field(ge=0, le=1)
    escalation_needed: bool