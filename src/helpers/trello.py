import json
from typing import List
from random import choice
import requests

from trello import TrelloClient

from src.helpers.board import BoardHelper
from src.constants import TicketStatus
from src.models import Ticket

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}

COLORS = ["green", "yellow", "orange", "red", "purple", "blue", "sky", "lime", "pink", "black"]

class CustomTrelloClient(TrelloClient):
    # Patch, because the base one is not working
    def __init__(self, api_key, token):
        self.api_key = api_key
        self.token = token

    def add_card(self, name, desc, list_id, label_id):
        url = f"https://api.trello.com/1/cards"
        query_params = {
            "key": self.api_key,
            "token": self.token,
            "name": name,
            "desc": desc,
            "idList": list_id,
            "idLabels": [label_id],
        }
        res = requests.post(url, headers=HEADERS, params=query_params)
        # print("Response from adding card to trello board: " + str(res.json()))

    def fetch_json(
        self,
        uri_path,
        http_method="GET",
        headers=None,
        query_params=None,
        post_args=None,
        files=None,
    ):
        if headers is None:
            headers = HEADERS
        if post_args is None:
            post_args = {}
        if query_params is None:
            query_params = {}
        if http_method in ("POST", "PUT", "DELETE") and not files:
            headers["Content-Type"] = "application/json; charset=utf-8"

        data = None
        if post_args:
            data = json.dumps(post_args)

        query_params["key"] = self.api_key
        query_params["token"] = self.token

        url = f"https://api.trello.com/1/{uri_path}"
        response = requests.request(
            http_method, url, headers=headers, params=query_params, data=data
        )
        return response.json()


class TrelloHelper(BoardHelper):
    def __init__(self, trello_api_key, trello_token, trello_board_id):
        self.client = CustomTrelloClient(
            api_key=trello_api_key,
            token=trello_token,
        )

        board = self.client.get_board(trello_board_id)
        self.board_id = trello_board_id
        self.list_ids = {list.name: list.id for list in board.list_lists()}
        expected_values = [v.value for v in TicketStatus]
        for val in expected_values:
            if val not in self.list_ids:
                print(
                    f"Error: List {val} not found. Make sure you have the correct list names {expected_values}."
                )
                exit(1)

    def get_ticket(self, ticket_id) -> Ticket:
        card = self.client.get_card(ticket_id)
        return Ticket(
            id=card.id,
            title=card.name,
            description=card.description,
            assignee_id=card.labels[0].id if card.labels else None,
        )

    def get_tickets_todo_list(self) -> List[Ticket]:
        cards = self.client.get_list(
            self.list_ids[TicketStatus.TODO.value]
        ).list_cards()
        if not cards:
            return []

        return [
            Ticket(
                id=card.id,
                title=card.name,
                description=card.description,
                assignee_id=card.labels[0].id if card.labels else "unassigned",
            )
            for card in cards
        ]

    def get_waiting_for_review_tickets(self) -> List[Ticket]:
        cards = self.client.get_list(
            self.list_ids[TicketStatus.READY_FOR_REVIEW.value]
        ).list_cards()
        if not cards:
            return []

        return [
            Ticket(
                id=card.id,
                title=card.name,
                description=card.description,
                assignee_id=card.labels[0].id if card.labels else "unassigned",
            )
            for card in cards
        ]

    def move_to_waiting_for_review(self, ticket_id):
        ticket = self.client.get_card(ticket_id)
        ticket.change_list(self.list_ids[TicketStatus.READY_FOR_REVIEW.value])

    def move_to_reviewed(self, ticket_id):
        ticket = self.client.get_card(ticket_id)
        ticket.change_list(self.list_ids[TicketStatus.REVIEWED.value])

    def move_to_approved(self, ticket_id):
        ticket = self.client.get_card(ticket_id)
        ticket.change_list(self.list_ids[TicketStatus.APPROVED.value])

    def move_to_wip(self, ticket_id):
        ticket = self.client.get_card(ticket_id)
        ticket.change_list(self.list_ids[TicketStatus.WIP.value])

    def push_tickets_to_backlog_and_assign(self, tickets: List[Ticket]) -> List[Ticket]:
        interns = self.get_intern_list()
        ticket_list = []
        for ticket in tickets:
            assignee = choice(interns)
            print(f"Assigning {ticket.title} to {assignee}")
            ticket.assignee_id = assignee
            ticket.status = TicketStatus.BACKLOG
            print(f"Adding card to list {self.list_ids[TicketStatus.BACKLOG.value]}")
            # Create a card in the backlog
            self.client.add_card(
                ticket.title,
                ticket.description,
                self.list_ids[TicketStatus.BACKLOG.value],
                assignee,
            )
            ticket_list.append(ticket)

        return ticket_list

    def get_intern_list(self):
        return [label.id for label in self.client.get_board(self.board_id).get_labels()]

    def create_intern(self, name):
        label = self.client.get_board(self.board_id).add_label(name, color=choice(COLORS))
        return label.id

    # TESTING METHODS

    def move_to_todo(self, ticket_id):
        ticket = self.client.get_card(ticket_id)
        ticket.change_list(self.list_ids[TicketStatus.TODO.value])

    def get_last_ticket(self):
        return self.client.get_list(self.list_ids[TicketStatus.BACKLOG.value]).list_cards()[-1]

    def delete_ticket(self, ticket_id):
        self.client.get_board(self.board_id).get_card(ticket_id).delete()

    def fire_intern(self, intern_id):
        self.client.get_board(self.board_id).delete_label(intern_id)
