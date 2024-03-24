from dotenv import load_dotenv
import os

from trello import create_oauth_token

from gh_helper import GHHelper
from trello_helper import TrelloHelper
from intern import Intern
from architect import Architect
from reviewer import Reviewer

load_dotenv()

gh_repo = os.getenv("GITHUB_REPO_URL")
gh_api_token = os.getenv("GITHUB_TOKEN")
trello_api_key = os.getenv("TRELLO_API_KEY")
trello_api_secret = os.getenv("TRELLO_API_SECRET")
trello_token = os.getenv("TRELLO_TOKEN")
trello_board_id = os.getenv("TRELLO_BOARD_ID")

if gh_repo is None:
    gh_repo = input("Enter the GitHub repo URL: ")
if gh_api_token is None:
    gh_api_token = input("Enter your GitHub Personnal Access token: ")

if trello_api_key is None:
    trello_api_key = input("Enter your Trello API key: ")
if trello_api_secret is None:
    trello_api_secret = input("Enter your Trello API secret: ")
if trello_token is None:
    auth_token = create_oauth_token(key=trello_api_key, secret=trello_api_secret, name='Trello API')
    trello_token = auth_token['oauth_token']
if trello_board_id is None:
    trello_board_id = input("Enter your Trello Board ID: ")


# Write them back to the .env file
with open(".env", "w") as f:
    f.write(f"GITHUB_REPO_URL={gh_repo}\n")
    f.write(f"GITHUB_TOKEN={gh_api_token}\n")
    f.write(f"TRELLO_API_KEY={trello_api_key}\n")
    f.write(f"TRELLO_API_SECRET={trello_api_secret}\n")
    f.write(f"TRELLO_TOKEN={trello_token}\n")
    f.write(f"TRELLO_BOARD_ID={trello_board_id}\n")


gh_helper = GHHelper(gh_api_token, gh_repo)
trello_helper = TrelloHelper(trello_api_key, trello_token, trello_board_id)

print(trello_helper.get_backlog_tickets())

# Step 1: With User input (streamit), define tickets, push to Trello's Backlog
architect = Architect("dave")
intern1 = Intern("alex")
intern2 = Intern("bob")
while True:
    # Console interface/Chat with 
    architect.start_cutting_tickets_for_interns(trello_helper)

    # Show Trello's Backlog: everyone is like "WOW!"

    # Step 2: Let's get to work (3 threads) (show dashboard/console to make refresh queries + Trello and GH updates)
    reviewer = Reviewer("charlie")
    intern1.run()
    intern2.run()
    reviewer.run()
