from github import Auth, Github


class GHHelper:
    def __init__(self, gh_api_token, gh_repo):
        auth = Auth.Token(gh_api_token)
        self.gh = Github(auth=auth)
        print("GHHelper initialized")
        try:
            self.repo = self.gh.get_repo(gh_repo)
            print(f"Selected repo: {self.repo.name}")
        except Exception as e:
            print(f"Error: {e}")

    def list_open_prs(self):
        return self.repo.get_pulls(state="open")

    def get_comments(self, pr):
        pr = self.repo.get_pull(pr)
        return pr.get_issue_comments()

    def add_comment(self, pr, comment):
        pr = self.repo.get_pull(pr)
        pr.create_issue_comment(comment)

    def mark_pr_as_approved(self, pr):
        pr = self.repo.get_pull(pr)
        pr.create_review(event="APPROVE")

    def push_changes(self, branch_name, comment):
        self.repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=self.repo.get_branch("main").commit.sha)
        self.repo.create_pull(title=branch_name, body=comment, head=branch_name, base="main")

    def get_entire_codebase(self):
        contents = self.repo.get_contents("")
        if not isinstance(contents, list):
            contents = [contents]

        codebase = {}
        for file in contents:
            try:
                codebase[file.path] = file.decoded_content.decode("utf-8")
            except Exception as e:
                pass
        return codebase

    def get_file_content(self, file):
        contents = self.repo.get_contents(file)
        if isinstance(contents, list):
            contents = contents[0]

        return contents.decoded_content.decode("utf-8")
