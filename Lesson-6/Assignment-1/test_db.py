from database.ticket_repository import create_ticket

ticket_id = create_ticket(
    "Can I use Docker?"
)

print(ticket_id)