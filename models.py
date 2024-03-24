from typing import Dict
from pydantic import BaseModel


class Ticket(BaseModel):
    id: int
    title: str
    description: str
    status: str
    assignee_id: int


class PR(BaseModel):
    id: int
    ticket_id: int
    assignee_id: int


class Codebase(BaseModel):
    files: Dict[str, str]