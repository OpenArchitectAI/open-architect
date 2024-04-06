from dotenv import load_dotenv
from threading import Thread
import os

from src.helpers.github import GHHelper
from src.helpers.trello import TrelloHelper

from src.agents.intern import Intern
from src.agents.reviewer import Reviewer

load_dotenv()

gh_repo = os.getenv("GITHUB_REPO_URL")
gh_api_token_intern = os.getenv("GITHUB_TOKEN_INTERN")
gh_api_token_reviewer = os.getenv("GITHUB_TOKEN_REVIEWER")
trello_api_key = os.getenv("TRELLO_API_KEY")
trello_api_secret = os.getenv("TRELLO_API_SECRET")
trello_token = os.getenv("TRELLO_TOKEN")
trello_board_id = os.getenv("TRELLO_BOARD_ID")

if (
    gh_repo is None
    or gh_api_token_intern is None
    or gh_api_token_reviewer is None
    or trello_api_key is None
    or trello_api_secret is None
    or trello_token is None
    or trello_board_id is None
):
    print(
        "Please run the init_connections.py script to set up the environment variables"
    )

gh_helper_intern = GHHelper(gh_api_token_intern, gh_repo)
gh_helper_reviewer = GHHelper(gh_api_token_reviewer, gh_repo)
trello_helper = TrelloHelper(trello_api_key, trello_token, trello_board_id)

intern = Intern("alex", gh_helper=gh_helper_intern, board_helper=trello_helper)
reviewer = Reviewer(
    "charlie",
    gh_helper=gh_helper_reviewer,
    board_helper=trello_helper,
)

intern_thread = Thread(target=intern.run)
reviewer_thread = Thread(target=reviewer.run)

# Step 1: With User input (streamit), define tickets, push to Trello's Backlog

while True:
    # Step 2: Let's get to work (n + 1 threads)
    intern_thread.start()
    reviewer_thread.start()
