from typing import List
from src.models import Ticket


class BoardHelper:
    def __init__(self):
        raise NotImplementedError("This is an interface class")
    
    def get_ticket(self, ticket_id) -> Ticket:
        raise NotImplementedError("This is an interface class")

    def get_tickets_todo_list(self) -> List[Ticket]:
        raise NotImplementedError("This is an interface class")

    def get_waiting_for_review_tickets(self) -> List[Ticket]:
        raise NotImplementedError("This is an interface class")

    def move_to_waiting_for_review(self, ticket_id):
        raise NotImplementedError("This is an interface class")

    def move_to_reviewed(self, ticket_id):
        raise NotImplementedError("This is an interface class")

    def move_to_approved(self, ticket_id):
        pass

    def move_to_wip(self, ticket_id):
        raise NotImplementedError("This is an interface class")

    def move_to_backlog(self, ticket_id):
        raise NotImplementedError("This is an interface class")

    def push_tickets_to_backlog_and_assign(self, tickets: List[Ticket]) -> List[Ticket]:
        raise NotImplementedError("This is an interface class")

    def assign_ticket(self, ticket_id, assignee_id):
        raise NotImplementedError("This is an interface class")
    
    def get_intern_list(self):
        raise NotImplementedError("This is an interface class")
    
    def create_intern(self, name):
        raise NotImplementedError("This is an interface class")
