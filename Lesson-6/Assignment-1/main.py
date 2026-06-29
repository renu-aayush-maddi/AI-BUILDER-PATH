# import os
# import io    

# from tkinter import Image
# from PIL import Image
# from dotenv import load_dotenv


# from langchain_core.messages import HumanMessage

# from langgraph.graph import StateGraph, START,END
# from langgraph.prebuilt import ToolNode
# from langgraph.checkpoint.memory import MemorySaver
# from langgraph.types import RetryPolicy



# #imports

# from tools.tools import (read_document,web_search)
# from core.state import SupportState
# from core.models import (AgentResponse)
# from core.llm import llm
# # from graph.routers import (router,it_tools_router,finance_tools_router)
# from graph.routers import (router,tools_router,return_to_agent_router)
# from agents.supervisor import supervisor_node
# # from agents.it_agent import it_agent_node
# # from agents.finance_agent import finance_agent_node
# from agents.department_agent import department_agent_node
# from nodes.ticket_handler import ticket_handler_node

# load_dotenv()


# # ENVIRONMENT

# if not os.getenv("OPENAI_API_KEY"):
#     raise ValueError("OPENAI_API_KEY missing")

# if not os.getenv("TAVILY_API_KEY"):
#     raise ValueError("TAVILY_API_KEY missing")

# # Optional LangSmith tracing
# if os.getenv("LANGCHAIN_API_KEY"):

#     os.environ["LANGCHAIN_TRACING_V2"] = "true"
#     os.environ["LANGCHAIN_PROJECT"] = "multi-agent-support-system"

# else:
#     os.environ["LANGCHAIN_TRACING_V2"] = "false"




# # TOOL NODES

# common_tool_node = ToolNode([read_document,web_search])

# # =========================================================
# # GRAPH
# # =========================================================

# workflow = StateGraph(SupportState)

# # =========================================================
# # NODES
# # =========================================================

# workflow.add_node("supervisor",supervisor_node,retry=RetryPolicy(max_attempts=3))

# # workflow.add_node(
# #     "it_agent",
# #     it_agent_node,
# #     retry=RetryPolicy(max_attempts=3),
# # )

# # workflow.add_node(
# #     "finance_agent",
# #     finance_agent_node,
# #     retry=RetryPolicy(max_attempts=3),
# # )
# workflow.add_node("department_agent",department_agent_node,retry=RetryPolicy(max_attempts=3),)

# workflow.add_node("ticket_handler",ticket_handler_node)


# # workflow.add_node("it_tools", common_tool_node)
# # workflow.add_node("finance_tools", common_tool_node)
# workflow.add_node("tools",common_tool_node)



# # =========================================================
# # START
# # =========================================================

# workflow.add_edge(START, "supervisor")

# # =========================================================
# # CONDITIONAL ROUTING
# # =========================================================

# # workflow.add_conditional_edges(
# #     "supervisor",
# #     router,
# #     {
# #         "it": "it_agent",
# #         "finance": "finance_agent"
# #     },
# # )

# workflow.add_conditional_edges(
#     "supervisor",
#     router,
#     {
#         "department_agent": "department_agent"
#     },
# )

# workflow.add_conditional_edges(
#     "department_agent",
#     tools_router,
#     {
#         "tools": "tools",
#         "complete": "ticket_handler",
#     },
# )

# workflow.add_conditional_edges(
#     "tools",
#     return_to_agent_router,
#     {
#         "department_agent": "department_agent"
#     },
# )


# # =========================================================
# # IT FLOW
# # =========================================================

# # workflow.add_conditional_edges(
# #     "it_agent",
# #     it_tools_router,
# #     {
# #         "it_tools": "it_tools",
# #         "end": "ticket_handler",
# #     },
# # )

# # workflow.add_edge("it_tools", "it_agent")

# # =========================================================
# # FINANCE FLOW
# # =========================================================

# # workflow.add_conditional_edges(
# #     "finance_agent",
# #     finance_tools_router,
# #     {
# #         "finance_tools": "finance_tools",
# #         "end": "ticket_handler",
# #     },
# # )

# # workflow.add_edge("finance_tools", "finance_agent")

# workflow.add_edge("ticket_handler",END)

# # =========================================================
# # MEMORY
# # =========================================================

# memory = MemorySaver()


# support_app = workflow.compile(
#     checkpointer=memory
# )

# # support_app = workflow.compile(checkpointer=memory)


# # VISUALIZE GRAPH
# png_data = support_app.get_graph().draw_mermaid_png()
# img = Image.open(io.BytesIO(png_data))
# img.show()


# # RUN CHAT
# import uuid
# def run_chat():

#     config = {
#         "configurable": {
#             "thread_id": "aayush"
#         }
#     }

#     print("\nSupport Assistant Started")
#     print("Type 'exit' to quit\n")

#     while True:

#         query = input("You: ")

#         if query.lower() in ["exit", "quit"]:
#             break

#         for event in support_app.stream(

#             {
#                 "messages": [
#                     HumanMessage(content=query)
#                 ],
#                 "departments": [],
#                 "current_department": "",
#                 "next_action": "",
#                 "tools_used": [],
#                 "resolved": False,
#                 "escalation_needed": False,
#                 "confidence": 0,
#                 "final_response": "",
#                 "ticket_id": "",

#             },

#             config=config,
#             stream_mode="updates",
#         ):
#             pass

#         final_state = support_app.get_state(config)

#         print("\nBot:")
#         print(final_state.values["final_response"])
#         print()


# if __name__ == "__main__":
#     run_chat()



import os
import io    

from tkinter import Image
from PIL import Image
from dotenv import load_dotenv

from langfuse import get_client
from langfuse.langchain import CallbackHandler

from langchain_core.messages import HumanMessage

from langgraph.graph import StateGraph, START,END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import RetryPolicy
from langfuse.langchain import CallbackHandler

from nemoguardrails import RailsConfig, LLMRails
from langchain_core.messages import AIMessage



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

current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, "config")

print("\n--- PATH DIAGNOSTICS ---")
print(f"Expected Config Path: {config_path}")
print(f"Does Python see the folder? {os.path.exists(config_path)}")
print(f"Folders/Files next to main.py: {os.listdir(current_dir)}")
print("------------------------\n")

# Initialize Guardrails
rails_config = RailsConfig.from_path(config_path)
guardrails = LLMRails(rails_config)
# ---------------------------------------

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



def guardrail_node(state: SupportState):
    user_query = state["messages"][-1].content
    
    # Run the query through NeMo Guardrails
    rail_response = guardrails.generate(messages=[{
        "role": "user", 
        "content": user_query
    }])
    
    response_text = rail_response["content"]
    
    # Check if the guardrail triggered our policy block
    if "Blocked by Policy" in response_text:
        return {
            "messages": [AIMessage(content=response_text)],
            "final_response": response_text,
            "resolved": True,           
            "next_action": "blocked"    
        }
        
    # If the input is safe, proceed to the supervisor
    return {
        "next_action": "supervisor"
    }



# TOOL NODES

common_tool_node = ToolNode([read_document,web_search])

# =========================================================
# GRAPH
# =========================================================

workflow = StateGraph(SupportState)

# =========================================================
# NODES
# =========================================================

workflow.add_node("guardrail", guardrail_node)

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

workflow.add_edge(START, "guardrail")



# =========================================================
# GUARDRAIL ROUTING
# =========================================================

def guardrail_router(state: SupportState):
    if state.get("next_action") == "blocked":
        return "ticket_handler" # Skip to the end
    return "supervisor"         # Proceed normally

workflow.add_conditional_edges(
    "guardrail",
    guardrail_router,
    {
        "supervisor": "supervisor",
        "ticket_handler": "ticket_handler"
    }
)
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


import uuid

def run_chat():
    
    # Generate a unique session ID for the entire conversation
    session_id = str(uuid.uuid4())
    
    # Initialize the global client to handle connections and flushing
    langfuse = get_client()
    langfuse.auth_check() # This will crash instantly if your .env keys are wrong

    print("\nSupport Assistant Started")
    print("Type 'exit' to quit\n")

    while True:
        query = input("You: ")

        if query.lower() in ["exit", "quit"]:
            break

        # 1. Initialize the Langfuse handler (NO ARGUMENTS ALLOWED in v4)
        langfuse_handler = CallbackHandler()

        # 2. Pass session and user IDs via the "metadata" dictionary in LangGraph
        run_config = {
            "configurable": {
                "thread_id": "aayush"
            },
            "callbacks": [langfuse_handler],
            "metadata": {
                "langfuse_session_id": session_id,
                "langfuse_user_id": "aayush"
            }
        }

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
            config=run_config, # Pass the config with Langfuse here
            stream_mode="updates",
        ):
            pass

        final_state = support_app.get_state(run_config)

        print("\nBot:")
        print(final_state.values["final_response"])
        print()
        
        # 3. Flush using the global client, not the handler
        langfuse.flush()

if __name__ == "__main__":
    run_chat()