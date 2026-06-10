import os
import io    

from tkinter import Image
from PIL import Image
from dotenv import load_dotenv


from langchain_core.messages import HumanMessage

from langgraph.graph import StateGraph, START,END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import RetryPolicy



#imports

from tools.tools import (read_document,web_search)
from core.state import SupportState
from core.models import (AgentResponse)
from core.llm import llm
# from graph.routers import (router,it_tools_router,finance_tools_router)
from graph.routers import (router,tools_router,return_to_agent_router)
from agents.supervisor import supervisor_node
# from agents.it_agent import it_agent_node
# from agents.finance_agent import finance_agent_node
from agents.department_agent import department_agent_node
from nodes.ticket_handler import ticket_handler_node

load_dotenv()


# ENVIRONMENT

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY missing")

if not os.getenv("TAVILY_API_KEY"):
    raise ValueError("TAVILY_API_KEY missing")

# Optional LangSmith tracing
if os.getenv("LANGCHAIN_API_KEY"):

    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "multi-agent-support-system"

else:
    os.environ["LANGCHAIN_TRACING_V2"] = "false"




# TOOL NODES

common_tool_node = ToolNode([read_document,web_search])

# =========================================================
# GRAPH
# =========================================================

workflow = StateGraph(SupportState)

# =========================================================
# NODES
# =========================================================

workflow.add_node("supervisor",supervisor_node,retry=RetryPolicy(max_attempts=3))

# workflow.add_node(
#     "it_agent",
#     it_agent_node,
#     retry=RetryPolicy(max_attempts=3),
# )

# workflow.add_node(
#     "finance_agent",
#     finance_agent_node,
#     retry=RetryPolicy(max_attempts=3),
# )
workflow.add_node("department_agent",department_agent_node,retry=RetryPolicy(max_attempts=3),)

workflow.add_node("ticket_handler",ticket_handler_node)


# workflow.add_node("it_tools", common_tool_node)
# workflow.add_node("finance_tools", common_tool_node)
workflow.add_node("tools",common_tool_node)



# =========================================================
# START
# =========================================================

workflow.add_edge(START, "supervisor")

# =========================================================
# CONDITIONAL ROUTING
# =========================================================

# workflow.add_conditional_edges(
#     "supervisor",
#     router,
#     {
#         "it": "it_agent",
#         "finance": "finance_agent"
#     },
# )

workflow.add_conditional_edges(
    "supervisor",
    router,
    {
        "department_agent": "department_agent"
    },
)

workflow.add_conditional_edges(
    "department_agent",
    tools_router,
    {
        "tools": "tools",
        "complete": "ticket_handler",
    },
)

workflow.add_conditional_edges(
    "tools",
    return_to_agent_router,
    {
        "department_agent": "department_agent"
    },
)


# =========================================================
# IT FLOW
# =========================================================

# workflow.add_conditional_edges(
#     "it_agent",
#     it_tools_router,
#     {
#         "it_tools": "it_tools",
#         "end": "ticket_handler",
#     },
# )

# workflow.add_edge("it_tools", "it_agent")

# =========================================================
# FINANCE FLOW
# =========================================================

# workflow.add_conditional_edges(
#     "finance_agent",
#     finance_tools_router,
#     {
#         "finance_tools": "finance_tools",
#         "end": "ticket_handler",
#     },
# )

# workflow.add_edge("finance_tools", "finance_agent")

workflow.add_edge("ticket_handler",END)

# =========================================================
# MEMORY
# =========================================================

memory = MemorySaver()


support_app = workflow.compile(
    checkpointer=memory
)

# support_app = workflow.compile(checkpointer=memory)


# VISUALIZE GRAPH
png_data = support_app.get_graph().draw_mermaid_png()
img = Image.open(io.BytesIO(png_data))
img.show()


# RUN CHAT
import uuid
def run_chat():

    config = {
        "configurable": {
            "thread_id": "aayush"
        }
    }

    print("\nSupport Assistant Started")
    print("Type 'exit' to quit\n")

    while True:

        query = input("You: ")

        if query.lower() in ["exit", "quit"]:
            break

        for event in support_app.stream(

            {
                "messages": [
                    HumanMessage(content=query)
                ],
                "departments": [],
                "current_department": "",
                "next_action": "",
                "tools_used": [],
                "resolved": False,
                "escalation_needed": False,
                "confidence": 0,
                "final_response": "",
                "ticket_id": "",

            },

            config=config,
            stream_mode="updates",
        ):
            pass

        final_state = support_app.get_state(config)

        print("\nBot:")
        print(final_state.values["final_response"])
        print()


if __name__ == "__main__":
    run_chat()