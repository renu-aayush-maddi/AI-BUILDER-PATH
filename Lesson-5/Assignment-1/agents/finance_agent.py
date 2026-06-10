from langchain_core.messages import SystemMessage

from core.llm import llm
from core.state import SupportState

from tools.tools import (read_document,web_search)


finance_llm = llm.bind_tools([
    read_document,
    web_search,
])


def finance_agent_node(state: SupportState):

    messages = [
        SystemMessage(
            content="""
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
        )
    ] + state["messages"]

    response = finance_llm.invoke(messages)
    

    needs_escalation = ("ESCALATE_TO_HUMAN"in response.content)
    

    return {
    "messages": [response],
    "final_response":"" if needs_escalation else response.content,
    "resolved": not needs_escalation
    }