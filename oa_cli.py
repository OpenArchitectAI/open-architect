import argparse
from dotenv import load_dotenv
from threading import Thread
import os
from src.helpers.github import GHHelper
from src.helpers.trello import TrelloHelper
from src.agents.intern import Intern
from src.agents.reviewer import Reviewer


def start_intern(gh_helper_intern, trello_helper):
    intern = Intern("Alex", gh_helper=gh_helper_intern, board_helper=trello_helper)
    intern_thread = Thread(target=intern.run)
    intern_thread.start()


def start_reviewer(gh_helper_reviewer, trello_helper):
    reviewer = Reviewer(
        "Charlie", gh_helper=gh_helper_reviewer, board_helper=trello_helper
    )
    reviewer_thread = Thread(target=reviewer.run)
    reviewer_thread.start()


def main():
    parser = argparse.ArgumentParser(description="Open Architect CLI")
    parser.add_argument("command", choices=["run"], help="Command to execute")
    parser.add_argument(
        "agents", nargs="+", choices=["intern", "reviewer"], help="Agents to run"
    )
    args = parser.parse_args()

    load_dotenv()

    gh_repo = os.getenv("GITHUB_REPO_URL")
    gh_api_token_intern = os.getenv("GITHUB_TOKEN_INTERN")
    gh_api_token_reviewer = os.getenv("GITHUB_TOKEN_REVIEWER")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    trello_api_key = os.getenv("TRELLO_API_KEY")
    trello_api_secret = os.getenv("TRELLO_API_SECRET")
    trello_token = os.getenv("TRELLO_TOKEN")
    trello_board_id = os.getenv("TRELLO_BOARD_ID")

    if (
        gh_repo is None
        or gh_api_token_intern is None
        or gh_api_token_reviewer is None
        or openai_api_key is None
        or trello_api_key is None
        or trello_api_secret is None
        or trello_token is None
        or trello_board_id is None
    ):
        print(
            "Please run the init_connections.py script to set up the environment variables"
        )
        return

    gh_helper_intern = GHHelper(gh_api_token_intern, gh_repo)
    gh_helper_reviewer = GHHelper(gh_api_token_reviewer, gh_repo)
    trello_helper = TrelloHelper(trello_api_key, trello_token, trello_board_id)

    if args.command == "run":
        for agent in args.agents:
            if agent == "intern":
                start_intern(gh_helper_intern, trello_helper)
            elif agent == "reviewer":
                start_reviewer(gh_helper_reviewer, trello_helper)


if __name__ == "__main__":
    main()
