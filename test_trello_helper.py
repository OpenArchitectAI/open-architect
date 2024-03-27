from dotenv import load_dotenv
import os

from src.models import Ticket
from src.helpers.trello import TrelloHelper

load_dotenv()

trello_api_key = os.getenv("TRELLO_API_KEY")
trello_token = os.getenv("TRELLO_TOKEN")
trello_board_id = os.getenv("TRELLO_BOARD_ID")

if trello_api_key is None or trello_token is None or trello_board_id is None:
    print("Please run the start.py script to set up the environment variables")

trello_helper = TrelloHelper(trello_api_key, trello_token, trello_board_id)

## Step 0: Create an intern
new_intern = trello_helper.create_intern("Test Intern")

## Step 1: Get the available "candidates" (interns) from Trello
interns = trello_helper.get_intern_list()
print("ok" if interns[-1] else "not ok")

## Step 2: Create a ticket and assign it to an intern
new_ticket = Ticket(
    title="Test Ticket",
    description="This is a test ticket",
    assignee_id=new_intern,
)
created_ticket = trello_helper.push_tickets_to_backlog_and_assign([new_ticket])[-1]
print("ok" if created_ticket.title == new_ticket.title else "not ok")
trello_helper.move_to_todo(trello_helper.get_last_ticket().id)

## Step 3: Get the tickets from the To Do list
tickets = trello_helper.get_tickets_todo_list()
print("ok" if tickets[-1] else "not ok")

## Step 4: Cleanup
trello_helper.delete_ticket(tickets[-1].id)
trello_helper.fire_intern(new_intern)
print("Done!")
