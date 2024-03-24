from intern.main import Intern
from dotenv import load_dotenv
import os
from models import Ticket
import openai, json

openai.api_key = json.loads(open("creds.json").read())["openai"]

load_dotenv()

gh_repo = os.getenv("GITHUB_REPO_URL")
gh_api_token = os.getenv("GITHUB_TOKEN")

if gh_repo is None:
    gh_repo = input("Enter the GitHub repo URL: ")
if gh_api_token is None:
    gh_api_token = input("Enter your GitHub Personnal Access token: ")

intern1 = Intern("alex", gh_api_token, gh_repo, gh_repo)

intern1.ticket_backlog = [
    Ticket(
        id=1,
        title="Improve with intructions to start",
        description="Our README should be more detailed on how to start the project.",
        assignee_id=0,
        status="backlog",
    )
]
intern1.run()
