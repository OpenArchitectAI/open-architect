from intern.main import Intern
from dotenv import load_dotenv
import os
from models import Ticket
import openai, json

from gh_helper import GHHelper
from trello_helper import TrelloHelper

openai.api_key = json.loads(open("creds.json").read())["openai"]

load_dotenv()

gh_repo = os.getenv("GITHUB_REPO_URL")
gh_api_token = os.getenv("GITHUB_TOKEN")
trello_api_key = os.getenv("TRELLO_API_KEY")
trello_api_secret = os.getenv("TRELLO_API_SECRET")
trello_token = os.getenv("TRELLO_TOKEN")
trello_board_id = os.getenv("TRELLO_BOARD_ID")

if (
    gh_repo is None
    or gh_api_token is None
    or trello_api_key is None
    or trello_api_secret is None
    or trello_token is None
    or trello_board_id is None
):
    print(
        "Please run the init_connections.py script to set up the environment variables"
    )

gh_helper = GHHelper(gh_api_token, gh_repo)
trello_helper = TrelloHelper(trello_api_key, trello_token, trello_board_id)

intern1 = Intern("alex", gh_helper, trello_helper)

intern1.ticket_backlog = [
    Ticket(
        id="660056eb92fd3a0e455d8700",
        title="Add a route to stop the API - 2",
        description="This route should stop the API or even kill the process",
        assignee_id="65ffd377a46cfb71ed651901",
        status="backlog",
    )
]
intern1.run()
