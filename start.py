from dotenv import load_dotenv
import os
from helpers.trello_helper import TrelloHelper
from intern.main import Intern

# from architect import Architect
from reviewer.main import Reviewer

load_dotenv()

gh_repo = os.getenv("GITHUB_REPO_URL")
gh_api_token = os.getenv("GITHUB_TOKEN")

if gh_repo is None:
    gh_repo = input("Enter the GitHub repo URL: ")
if gh_api_token is None:
    gh_api_token = input("Enter your GitHub Personnal Access token: ")

# Write them back to the .env file
with open(".env", "a") as f:
    f.write(f"GITHUB_REPO_URL={gh_repo}\n")
    f.write(f"GITHUB_TOKEN={gh_api_token}\n")


# Step 1: With User input (streamit), define tickets, push to Trello's Backlog
# architect = Architect("dave")
# intern1 = Intern("alex")
# intern2 = Intern("bob")
while True:
    # Console interface/Chat with
    # architect.start_cutting_tickets_for_interns(TrelloHelper)

    # Show Trello's Backlog: everyone is like "WOW!"

    # Step 2: Let's get to work (3 threads) (show dashboard/console to make refresh queries + Trello and GH updates)
    reviewer = Reviewer(
        "charlie",
        gh_api_token=os.environ.get("GITHUB_TOKEN"),
        gh_repo=os.environ.get("GITHUB_REPO_URL"),
        trello_helper=TrelloHelper(),
    )
    # intern1.run()
    # intern2.run()
    reviewer.run()
