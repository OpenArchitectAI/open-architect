from enum import Enum

class TicketStatus(Enum):
    BACKLOG = "Backlog"
    WIP = "WIP"
    READY_FOR_REVIEW = "Ready for Review"
    REVIEWED = "Reviewed"
    APPROVED = "Approved"