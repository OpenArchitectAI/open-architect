from typing import Dict, List, Literal, Optional
from pydantic import BaseModel

from github.PullRequest import ReviewComment

ticket_stages = ["backlog", "todo", "wip", "review", "done"]


class Ticket(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    status: Optional[str] = None
    assignee_id: Optional[str] = None


class ModifiedFile(BaseModel):
    filename: str
    status: str
    additions: int
    deletions: int
    changes: int
    patch: str


# Todo: Use github.PullRequest class instead of this
class PR(BaseModel):
    id: int
    ticket_id: Optional[str] = None
    assignee_id: Optional[str] = None
    title: str
    description: str
    files_changed: List[ModifiedFile] = []


class CodeReview(BaseModel):
    pr: PR
    body: str
    event: Literal["APPROVE", "REQUEST_CHANGES", "COMMENT"]
    comments: List[ReviewComment] = []


class Codebase(BaseModel):
    files: Dict[str, str]
