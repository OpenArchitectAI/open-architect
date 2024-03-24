from github import Auth, Github, InputGitTreeElement, InputGitAuthor

from models import Codebase


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

    def push_changes(self, branch_name, diff):
        # Parse the diff and create blobs for each modified file
        # Hoping that the diff is properly formatted

        modified_files = []
        for diff_block in diff.split("diff --git"):
            if diff_block.strip():
                lines = diff_block.strip().split("\n")
                file_path = lines[0].split(" b/")[1]
                blob_content = "\n".join(lines[5:])
                blob = self.repo.create_git_blob(blob_content, "utf-8")
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
        branch_name = "new-feature-9"
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
        pr_title = "New Feature Pull Request"
        pr_body = "Please review and merge the changes."
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
