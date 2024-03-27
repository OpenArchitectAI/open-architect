from dotenv import load_dotenv
import os


from src.helpers.github import GHHelper
from src.helpers.trello import TrelloHelper

from src.agents.architect import Architect

load_dotenv()

gh_repo = os.getenv("GITHUB_REPO_URL")
gh_api_token_reviewer = os.getenv("GITHUB_TOKEN_REVIEWER")
openai_api_key = os.getenv("OPENAI_API_KEY")
trello_api_key = os.getenv("TRELLO_API_KEY")
trello_api_secret = os.getenv("TRELLO_API_SECRET")
trello_token = os.getenv("TRELLO_TOKEN")
trello_board_id = os.getenv("TRELLO_BOARD_ID")

if (
    gh_repo is None
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

gh_helper = GHHelper(gh_api_token_reviewer, gh_repo)
trello_helper = TrelloHelper(trello_api_key, trello_token, trello_board_id)

architect = Architect(
    "sophia",
    gh_helper=gh_helper,
    trello_helper=trello_helper,
    openai_key=openai_api_key,
)

architect.run()