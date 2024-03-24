from dotenv import load_dotenv
import os

from helpers.gh_helper import GHHelper

load_dotenv()

gh_repo = os.getenv("GITHUB_REPO_URL")
gh_api_token = os.getenv("GITHUB_TOKEN")
if gh_repo is None or gh_api_token is None:
    print("Please run the start.py script to set up the environment variables")

gh = GHHelper(gh_api_token, gh_repo)

gh.list_open_prs()

print(gh.get_entire_codebase())
