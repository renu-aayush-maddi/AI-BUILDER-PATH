from langchain_core.messages import SystemMessage

from core.llm import llm
from core.state import SupportState

from tools.tools import (read_document,web_search)

it_llm = llm.bind_tools([read_document,web_search])


def it_agent_node(state: SupportState):

    messages = [
        SystemMessage(
            content="""
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
            """
        )
    ] + state["messages"]

    response = it_llm.invoke(messages)
    needs_escalation = ("ESCALATE_TO_HUMAN"in response.content)
    

    return {
    "messages": [response],
    "final_response":"" if needs_escalation else response.content,
    "resolved": not needs_escalation
    }