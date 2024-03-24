from github import Github

# Authentication is defined via github.Auth
from github import Auth

class GHHelper:
    def __init__(self, gh_api_token):
        auth = Auth.Token(gh_api_token)
        self.gh = Github(auth=auth)

    def list_open_prs(self, repo):
        print(f"Listing open PRs for {repo}")

    def get_comments(self, pr):
        print(f"Getting comments for PR {pr}")
    
    def add_comment(self, pr, comment):
        print(f"Adding comment {comment} to PR {pr}")

    def mark_pr_as_approved(self, pr):
        print(f"Marking PR {pr} as approved")

    def push_changes(self, repo):
        print(f"Pushing changes to {repo}")
