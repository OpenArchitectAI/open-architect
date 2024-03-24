from trello import TrelloClient


class TrelloHelper:
    def __init__(self):
        self.client = None

    def get_backlog_tickets(self):
        print("Getting backlog tickets")
        return []

    def get_waiting_for_review_tickets(self):
        print("Getting waiting for review tickets")

    def move_to_waiting_for_review(self, ticket):
        print(f"Moving ticket {ticket} to waiting for review")

    def mov_to_reviewed(self, ticket):
        print(f"Moving ticket {ticket} to reviewed")

    def move_to_done(self, ticket):
        print(f"Moving ticket {ticket} to done")

    def move_to_wip(self, ticket):
        print(f"Moving ticket {ticket} to WIP")
