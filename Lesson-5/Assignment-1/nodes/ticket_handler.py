from core.state import SupportState

from services.email_service import send_ticket_email

from database.ticket_repository import (
    resolve_ticket,
    update_status
)

from tools.email_sender import send_support_email


def ticket_handler_node(state: SupportState):

    print("\n========== TICKET HANDLER ==========")
    print("ticket_id:", state["ticket_id"])
    print("resolved:", state["resolved"])
    print("final_response:", state["final_response"])

    if state["resolved"]:

        print("RESOLVING TICKET")

        resolve_ticket(
            state["ticket_id"],
            state["final_response"]
        )

        return {}

    print("KEEPING TICKET OPEN")

    update_status(
        state["ticket_id"],
        "OPEN"
    )

    send_support_email(
        ticket_id=state["ticket_id"],
        question=state["messages"][0].content,
        department=state["departments"][0]
    )

    return {
        "final_response": (
            f"Ticket ID: {state['ticket_id']}\n\n"
            "Your issue could not be resolved automatically.\n\n"
            "The support team has been notified."
        )
    }