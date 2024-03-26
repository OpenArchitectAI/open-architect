from dotenv import load_dotenv
from threading import Thread
import os

from src.helpers.github import GHHelper
from src.helpers.trello import TrelloHelper

from src.agents.intern import Intern
from src.agents.reviewer import Reviewer

import src.chat_interface as chat_interface

load_dotenv()

gh_repo = os.getenv("GITHUB_REPO_URL")
<<<<<<< HEAD
gh_api_token_intern = os.getenv("GITHUB_TOKEN_INTERN")
gh_api_token_reviewer = os.getenv("GITHUB_TOKEN_REVIEWER")
=======
gh_api_token = os.getenv("GITHUB_TOKEN")
>>>>>>> 746ae7a (Integrate review with Trello)
openai_api_key = os.getenv("OPENAI_API_KEY")
trello_api_key = os.getenv("TRELLO_API_KEY")
trello_api_secret = os.getenv("TRELLO_API_SECRET")
trello_token = os.getenv("TRELLO_TOKEN")
trello_board_id = os.getenv("TRELLO_BOARD_ID")

if (
    gh_repo is None
<<<<<<< HEAD
    or gh_api_token_intern is None
    or gh_api_token_reviewer is None
=======
    or gh_api_token is None
>>>>>>> 746ae7a (Integrate review with Trello)
    or openai_api_key is None
    or trello_api_key is None
    or trello_api_secret is None
    or trello_token is None
    or trello_board_id is None
):
    print(
        "Please run the init_connections.py script to set up the environment variables"
    )


# Write them back to the .env file
with open(".env", "w") as f:
    f.write(f"GITHUB_REPO_URL={gh_repo}\n")
<<<<<<< HEAD
    f.write(f"GITHUB_TOKEN_INTERN={gh_api_token_intern}\n")
    f.write(f"GITHUB_TOKEN_REVIEWER={gh_api_token_reviewer}\n")
=======
    f.write(f"GITHUB_TOKEN={gh_api_token}\n")
>>>>>>> 746ae7a (Integrate review with Trello)
    f.write(f"OPENAI_API_KEY={openai_api_key}\n")
    f.write(f"TRELLO_API_KEY={trello_api_key}\n")
    f.write(f"TRELLO_API_SECRET={trello_api_secret}\n")
    f.write(f"TRELLO_TOKEN={trello_token}\n")
    f.write(f"TRELLO_BOARD_ID={trello_board_id}\n")

<<<<<<< HEAD
gh_helper_intern = GHHelper(gh_api_token_intern, gh_repo)
gh_helper_reviewer = GHHelper(gh_api_token_reviewer, gh_repo)
trello_helper = TrelloHelper(trello_api_key, trello_token, trello_board_id)

intern = Intern("alex", gh_helper=gh_helper_intern, trello_helper=trello_helper)
=======
gh_helper = GHHelper(gh_api_token, gh_repo)
trello_helper = TrelloHelper(trello_api_key, trello_token, trello_board_id)

# Step 1: With User input (streamit), define tickets, push to Trello's Backlog
# architect = Architect("dave")
intern1 = Intern("alex", gh_helper=gh_helper, trello_helper=trello_helper)
# intern2 = Intern("bob", gh_helper=gh_helper, trello_helper=trello_helper)
>>>>>>> 746ae7a (Integrate review with Trello)
reviewer = Reviewer(
    "charlie",
    gh_helper=gh_helper_reviewer,
    trello_helper=trello_helper,
)

intern_thread = Thread(target=intern.run)
reviewer_thread = Thread(target=reviewer.run)

# Step 1: With User input (streamit), define tickets, push to Trello's Backlog
# chat_interface.open_architect(trello_helper, gh_helper_reviewer)

while True:
<<<<<<< HEAD
    # Step 2: Let's get to work (n + 1 threads)
    intern_thread.start()
    reviewer_thread.start()
=======
    # Console interface/Chat with
    # architect.start_cutting_tickets_for_interns(TrelloHelper)

    # Show Trello's Backlog: everyone is like "WOW!"

    # Step 2: Let's get to work (3 threads) (show dashboard/console to make refresh queries + Trello and GH updates)
    # intern1.run()
    # intern2.run()
    reviewer.run()
>>>>>>> 746ae7a (Integrate review with Trello)
