from dotenv import load_dotenv
import os

from models import Ticket
from trello_helper import TrelloHelper

load_dotenv()

trello_api_key = os.getenv("TRELLO_API_KEY")
trello_token = os.getenv("TRELLO_TOKEN")
trello_board_id = os.getenv("TRELLO_BOARD_ID")

if trello_api_key is None or trello_token is None or trello_board_id is None:
    print("Please run the start.py script to set up the environment variables")

trello_helper = TrelloHelper(trello_api_key, trello_token, trello_board_id)

tickets = trello_helper.get_backlog_tickets()
print(tickets)

print(trello_helper.get_intern_list())

if tickets:
    assignees = [t.assignee_id for t in tickets]

    new_ticket = Ticket(
        title="Test Ticket",
        description="This is a test ticket",
        assignee_id=trello_helper.get_intern_list()[-1]
    )

    trello_helper.push_tickets_to_backlog_and_assign([new_ticket])

    ticket = trello_helper.get_backlog_tickets()[-1]

    print(ticket)

    # trello_helper.move_to_wip(ticket.id)