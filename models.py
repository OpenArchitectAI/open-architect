from typing import Dict, Optional
from pydantic import BaseModel


ticket_stages = ["backlog", "todo", "wip", "review", "done"]


class Ticket(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    status: Optional[str] = None
    assignee_id: str


class PR(BaseModel):
    id: int
    ticket_id: int
    assignee_id: int


class Codebase(BaseModel):
    files: Dict[str, str]
