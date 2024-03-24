from github import Auth, Github, InputGitTreeElement, InputGitAuthor

from models import CodeReview, Codebase


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

    def get_pr(self, pr_number):
        print("---get_pr---")
        try:
            pr = self.repo.get_pull(pr_number)
            return pr
        except Exception as e:
            print(f"Error fetching PR #{pr_number}: {e}")
            return None

    def get_comments(self, pr):
        pr = self.repo.get_pull(pr)
        return pr.get_issue_comments()

    def add_comment(self, pr, comment):
        pr = self.repo.get_pull(pr)
        pr.create_issue_comment(comment)

    def mark_pr_as_approved(self, pr):
        pr = self.repo.get_pull(pr)
        pr.create_review(event="APPROVE")        
        
    def submit_code_review(self, code_review: CodeReview):
        pr = self.repo.get_pull(number=code_review.pr.id)
        pr.create_review(
            event=code_review.event,
            body=code_review.body,
            comments=code_review.comments,
        )

    def push_changes(self, branch_name, pr_title, pr_body, new_files):
        # Parse the diff and create blobs for each modified file
        # Hoping that the diff is properly formatted

        modified_files = []
        for file_path, file_content in new_files.items():
            blob = self.repo.create_git_blob(file_content, "utf-8")
            modified_files.append(
                InputGitTreeElement(
                    path=file_path, mode="100644", type="blob", sha=blob.sha
                )
            )

        # Get the current commit's tree
        base_tree = self.repo.get_git_tree(sha=self.repo.get_commits()[0].sha)

        # Create a new tree with the modified files
        new_tree = self.repo.create_git_tree(modified_files, base_tree)

        # Create a new branch
        ref = self.repo.create_git_ref(
            f"refs/heads/{branch_name}", self.repo.get_commits()[0].sha
        )

        # Create a new commit with the new tree on the new branch
        author = InputGitAuthor("Open Architect", "openarchitect@gmail.com")

        commit_message = "Apply diff to multiple files"
        new_commit = self.repo.create_git_commit(
            commit_message,
            new_tree,
            [self.repo.get_git_commit(self.repo.get_commits()[0].sha)],
            author,
        )

        # Update the branch reference to point to the new commit
        ref.edit(sha=new_commit.sha)

        # Create a new pull request
        base_branch = "main"  # Replace with the target branch for the pull request
        head = f"{self.repo.owner.login}:{branch_name}"  # Update the head parameter
        pr = self.repo.create_pull(
            title=pr_title, body=pr_body, head=head, base=base_branch
        )

    def get_entire_codebase(self) -> Codebase:
        contents = self.repo.get_contents("")
        if not isinstance(contents, list):
            contents = [contents]

        codebase_dict = {}
        for file in contents:
            try:
                codebase_dict[file.path] = file.decoded_content.decode("utf-8")
            except Exception as e:
                pass

        codebase = Codebase(files=codebase_dict)

        return codebase

    def get_file_content(self, file):
        contents = self.repo.get_contents(file)
        if isinstance(contents, list):
            contents = contents[0]

        return contents.decoded_content.decode("utf-8")
