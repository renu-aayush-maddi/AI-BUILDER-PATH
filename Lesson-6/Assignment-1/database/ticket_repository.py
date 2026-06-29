import uuid
import psycopg


DB_CONFIG = {
    "host": "localhost",
    "port": 5469,
    "dbname": "support_system",
    "user": "postgres",
    "password": "aayush05"
}


def get_connection():
    return psycopg.connect(**DB_CONFIG)


def create_ticket(question):

    ticket_id = str(uuid.uuid4())

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                INSERT INTO support_tickets
                (
                    ticket_id,
                    question,
                    status
                )
                VALUES
                (
                    %s,
                    %s,
                    'OPEN'
                )
                """,
                (
                    ticket_id,
                    question
                )
            )

        conn.commit()

    return ticket_id


def update_department(ticket_id, department):

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                UPDATE support_tickets
                SET department=%s
                WHERE ticket_id=%s
                """,
                (
                    department,
                    ticket_id
                )
            )

        conn.commit()
        
def resolve_ticket(
    ticket_id,
    answer
):

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                UPDATE support_tickets
                SET
                    status='RESOLVED',
                    answer=%s,
                    updated_at=NOW()
                WHERE ticket_id=%s
                """,
                (
                    answer,
                    ticket_id
                )
            )

        conn.commit()

def update_status(ticket_id, status):

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                UPDATE support_tickets
                SET
                    status=%s,
                    updated_at=NOW()
                WHERE ticket_id=%s
                """,
                (
                    status,
                    ticket_id
                )
            )

        conn.commit()