from dotenv import load_dotenv
from random import randint
import os

from src.models import Ticket
from src.helpers.trello import TrelloHelper

load_dotenv()

N_TICKETS = 10

trello_api_key = os.getenv("TRELLO_API_KEY")
trello_api_secret = os.getenv("TRELLO_API_SECRET")
trello_token = os.getenv("TRELLO_TOKEN")
trello_board_id = os.getenv("TRELLO_BOARD_ID")

th = TrelloHelper(trello_api_key, trello_token, trello_board_id)

tickets = [
    Ticket(
        title="Test Ticket " + str(randint(0, 10000)),
        description="This is a test ticket",
    )
    for _ in range(N_TICKETS)
]
th.push_tickets_to_backlog_and_assign(tickets)
