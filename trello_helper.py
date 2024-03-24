import json
from typing import List
from random import choice
import requests

from trello import TrelloClient

from constants import TicketStatus
from models import Ticket

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}

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
        requests.post(url, headers=HEADERS, params=query_params)

    def fetch_json(
        self,
        uri_path,
        http_method='GET', headers=None, query_params=None, post_args=None, files=None):
        if headers is None:
            headers = HEADERS
        if post_args is None:
            post_args = {}
        if query_params is None:
            query_params = {}
        if http_method in ("POST", "PUT", "DELETE") and not files:
            headers['Content-Type'] = 'application/json; charset=utf-8'

        data = None
        if post_args:
            data = json.dumps(post_args)

        query_params['key'] = self.api_key
        query_params['token'] = self.token

        url = f"https://api.trello.com/1/{uri_path}"
        response = requests.request(http_method, url, headers=headers, params=query_params, data=data)
        return response.json()

class TrelloHelper:
    def __init__(self, trello_api_key, trello_token, trello_board_id):
        self.client = CustomTrelloClient(
            api_key=trello_api_key,
            token=trello_token,
        )

        print("TrelloHelper initialized")

        board = self.client.get_board(trello_board_id)
        print(f"Selected board: {board.name}")
        print(f"Board lists: {board.list_lists()}")
        self.list_ids = {list.name: list.id for list in board.list_lists()}

    def get_backlog_tickets(self):
        cards = self.client.get_list(self.list_ids[TicketStatus.BACKLOG.value])
        if not cards:
            return []
        
        return [Ticket(id=card.id, title=card.name, description=card.description, assignee_id=card.labels[0].id) for card in cards]

    def get_waiting_for_review_tickets(self):
        cards = self.client.get_list(self.list_ids[TicketStatus.READY_FOR_REVIEW.value])
        if not cards:
            return []
        
        return [Ticket(id=card.id, title=card.name, description=card.description, assignee_id=card.labels[0].id) for card in cards]

    def move_to_waiting_for_review(self, ticket_id):
        ticket = self.client.get_card(ticket_id)
        ticket.change_list(self.list_ids[TicketStatus.READY_FOR_REVIEW.value])

    def mov_to_reviewed(self, ticket_id):
        ticket = self.client.get_card(ticket_id)
        ticket.change_list(self.list_ids[TicketStatus.REVIEWED.value])

    def move_to_approved(self, ticket_id):
        ticket = self.client.get_card(ticket_id)
        ticket.change_list(self.list_ids[TicketStatus.APPROVED.value])

    def move_to_wip(self, ticket_id):
        ticket = self.client.get_card(ticket_id)
        ticket.change_list(self.list_ids[TicketStatus.WIP.value])

    def push_tickets_to_backlog_and_assign(self, tickets: List[Ticket], interns: str):
        for ticket in tickets:
            assignee = choice(interns)
            print(f"Assigning {ticket.title} to {assignee}")
            # Create a card in the backlog
            self.client.add_card(ticket.title, ticket.description, self.list_ids[TicketStatus.BACKLOG.value], assignee)
        
