from langchain_core.messages import SystemMessage

from core.llm import llm
from core.state import SupportState

from tools.tools import (read_document,web_search)

agent_llm = llm.bind_tools([read_document,web_search])


DEPARTMENT_PROMPTS = {

    "IT": """
    You are IT support agent.

    Use tools whenever needed.

    Use department="IT"

    If VPN → vpn_setup.txt
    If software → approved_software.txt
    If laptop → laptop_request.txt

    IMPORTANT:

    Answer ONLY using information available
    from the provided documents.

    If the answer cannot be determined
    from available documents, respond exactly:

    ESCALATE_TO_HUMAN
    """,

    "Finance": """
    You are Finance support agent.

    Use tools whenever needed.

    Use department="Finance"

    If reimbursement → reimbursement.txt
    If payroll → payroll.txt
    If budget → budget_report.txt

    IMPORTANT:

    Answer ONLY using information available
    from the provided documents.

    If the answer cannot be determined
    from available documents, respond exactly:

    ESCALATE_TO_HUMAN
    """
}


def department_agent_node(state: SupportState):

    department = state["current_department"]

    system_prompt = DEPARTMENT_PROMPTS[department]

    messages = [
        SystemMessage(content=system_prompt)
    ] + state["messages"]

    response = agent_llm.invoke(messages)

    needs_escalation = (
        "ESCALATE_TO_HUMAN" in response.content
    )

    return {
        "messages": [response],
        "final_response":
            "" if needs_escalation
            else response.content,
        "resolved": not needs_escalation
    }