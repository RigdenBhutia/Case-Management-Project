from datetime import datetime
from itertools import count
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Mock Ticketing System")

# In-memory store. It resets whenever the server restarts.
# Change case_id values to IDs that exist in your cases table.
tickets = {
    "T-1001": {"ticket_id": "T-1001", "case_id": 1, "status": "open",
               "comment": None, "updated_at": None},
    "T-1002": {"ticket_id": "T-1002", "case_id": 2, "status": "open",
               "comment": None, "updated_at": None},
}

_next_id = count(1003)


class TicketCreate(BaseModel):
    case_id: int


class TicketUpdate(BaseModel):
    status: str
    comment: Optional[str] = None


@app.post("/tickets", status_code=201)
def create_ticket(payload: TicketCreate):
    # One ticket per case: if one exists, return it instead of duplicating
    for t in tickets.values():
        if t["case_id"] == payload.case_id:
            return t
    ticket_id = f"T-{next(_next_id)}"
    tickets[ticket_id] = {
        "ticket_id": ticket_id,
        "case_id": payload.case_id,
        "status": "open",
        "comment": None,
        "updated_at": None,
    }
    return tickets[ticket_id]


@app.get("/tickets")
def find_tickets(case_id: Optional[int] = None):
    results = list(tickets.values())
    if case_id is not None:
        results = [t for t in results if t["case_id"] == case_id]
    return results


@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: str):
    ticket = tickets.get(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@app.put("/tickets/{ticket_id}")
def update_ticket(ticket_id: str, update: TicketUpdate):
    ticket = tickets.get(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket["status"] = update.status
    ticket["comment"] = update.comment
    ticket["updated_at"] = datetime.now().isoformat()
    return ticket