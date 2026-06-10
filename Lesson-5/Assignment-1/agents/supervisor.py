from langchain_core.messages import (HumanMessage,SystemMessage)

from core.llm import llm
from core.models import SupervisorDecision
from core.state import SupportState
from database.ticket_repository import create_ticket, update_department

structured_supervisor = llm.with_structured_output(SupervisorDecision)


def supervisor_node(state: SupportState):

    user_query = state["messages"][-1].content

    ticket_id = create_ticket(user_query)

    decision = structured_supervisor.invoke([
        SystemMessage(
            content="""
            You are a supervisor.

            Classify query into:
            - IT
            - Finance
            - Both

            Return departments list.
            """
        ),
        HumanMessage(content=user_query),
    ])

    departments = decision.departments
    
    update_department(ticket_id,departments[0])

    current_department = departments[0]

    next_action = "department_agent"

    return {
    "ticket_id": ticket_id,
    "departments": departments,
    "current_department": current_department,
    "next_action": next_action,
    "tools_used": ["supervisor_classification"]
}