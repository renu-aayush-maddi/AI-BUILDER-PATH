import operator
from typing import Annotated, List, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class SupportState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    departments: List[str]
    current_department: str
    next_action: str
    tools_used: Annotated[List[str], operator.add]
    resolved: bool
    escalation_needed: bool
    confidence: float
    final_response: str
    ticket_id: str