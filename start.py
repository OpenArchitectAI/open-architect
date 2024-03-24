from dotenv import load_dotenv
import os

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