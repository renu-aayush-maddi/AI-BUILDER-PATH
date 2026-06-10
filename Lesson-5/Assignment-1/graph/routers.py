# from core.state import SupportState


# def router(state: SupportState):
#     return state["next_action"]


# def it_tools_router(state: SupportState):

#     last_message = state["messages"][-1]

#     if hasattr(last_message, "tool_calls") and last_message.tool_calls:
#         return "it_tools"

#     return "end"


# def finance_tools_router(state: SupportState):

#     last_message = state["messages"][-1]

#     if hasattr(last_message, "tool_calls") and last_message.tool_calls:
#         return "finance_tools"

#     return "end"



from core.state import SupportState


def router(state: SupportState):
    return state["next_action"]


def tools_router(state: SupportState):

    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    return "complete"


def return_to_agent_router(state: SupportState):
    return "department_agent"