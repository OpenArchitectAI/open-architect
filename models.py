from typing import Dict, List, Literal, Optional
from pydantic import BaseModel

from github.PullRequest import ReviewComment

ticket_stages = ["backlog", "todo", "wip", "review", "done"]


class Ticket(BaseModel):
    id: int
    title: str
    description: str
    status: str
    assignee_id: int


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
    ticket_id: int
    assignee_id: int
    title: str
    description: str
    files_changed: List[ModifiedFile]


class CodeReview(BaseModel):
    pr: PR
    body: str
    event: Literal["APPROVE", "REQUEST_CHANGES", "COMMENT"]
    comments: List[ReviewComment]


class Codebase(BaseModel):
    files: Dict[str, str]
