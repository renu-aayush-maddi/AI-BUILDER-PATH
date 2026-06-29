# from core.state import SupportState

# from services.email_service import send_ticket_email

# from database.ticket_repository import (
#     resolve_ticket,
#     update_status
# )

# from tools.email_sender import send_support_email


# def ticket_handler_node(state: SupportState):

#     print("\n========== TICKET HANDLER ==========")
#     print("ticket_id:", state["ticket_id"])
#     print("resolved:", state["resolved"])
#     print("final_response:", state["final_response"])

#     if state["resolved"]:

#         print("RESOLVING TICKET")

#         resolve_ticket(
#             state["ticket_id"],
#             state["final_response"]
#         )

#         return {}

#     print("KEEPING TICKET OPEN")

#     update_status(
#         state["ticket_id"],
#         "OPEN"
#     )

#     send_support_email(
#         ticket_id=state["ticket_id"],
#         question=state["messages"][0].content,
#         department=state["departments"][0]
#     )

#     return {
#         "final_response": (
#             f"Ticket ID: {state['ticket_id']}\n\n"
#             "Your issue could not be resolved automatically.\n\n"
#             "The support team has been notified."
#         )
#     }


from core.state import SupportState
from services.email_service import send_ticket_email
from database.ticket_repository import resolve_ticket, update_status
from tools.email_sender import send_support_email

def ticket_handler_node(state: SupportState):
    print("\n========== TICKET HANDLER ==========")
    
    # SAFE LOOKUPS: Use .get() to prevent KeyErrors on skipped execution paths
    ticket_id = state.get("ticket_id", None)
    resolved = state.get("resolved", False)
    final_response = state.get("final_response", "")
    messages = state.get("messages", [])

    print("ticket_id:", ticket_id)
    print("resolved:", resolved)
    print("final_response:", final_response)

    if resolved:
        # Only interact with the database if a ticket was actually initialized
        if ticket_id:
            print("RESOLVING TICKET")
            resolve_ticket(ticket_id, final_response)
        else:
            print("NO TICKET CREATED (Blocked by Guardrail)")

        return {}

    print("KEEPING TICKET OPEN")

    if ticket_id:
        update_status(ticket_id, "OPEN")
        
        # Safely extract the original user question text
        user_question = messages[-1].content if messages else "Unknown Query"
        departments_list = state.get("departments", [])
        chosen_dept = departments_list[0] if departments_list else "General"

        send_support_email(
            ticket_id=ticket_id,
            question=user_question,
            department=chosen_dept
        )

    return {
        "final_response": (
            f"Ticket ID: {ticket_id if ticket_id else 'N/A'}\n\n"
            "Your issue could not be resolved automatically.\n\n"
            "The support team has been notified."
        )
    }