from typing import List
from reviewer.agents.code_review_generator import GeneratedCodeReview
from reviewer.processors import review_code

from models import PR, CodeReview, ModifiedFile, Ticket
from github.PullRequest import PullRequest

import time


class Reviewer:
    def __init__(self, name, gh_helper, trello_helper):
        self.name = name
        self.pr_backlog = []
        self.gh_helper = gh_helper
        self.trello_helper = trello_helper
        print(f"[REVIEWER] Hi, my name is {self.name}. I'm ready to review some bad code.")

    def refresh_pr_backlog(self):
        print("[REVIEWER] ---refresh_pr_backlog---")
        next_prs = [
            pr for pr in self.gh_helper.list_open_prs() if pr not in self.pr_backlog  
        ]
        print(f"[REVIEWER] next_prs: {[pr.title for pr in next_prs]}")
        self.pr_backlog.extend(next_prs)

    # def simplify_pr(self, raw_pr: PullRequest, ticket: Ticket) -> PR:
    #     files_changed = raw_pr.get_files()

    #     files_changed_with_diffs: List[ModifiedFile] = []
    #     for file in files_changed:
    #         files_changed_with_diffs.append(
    #             ModifiedFile(
    #                 filename=file.filename,
    #                 status=file.status,
    #                 additions=file.additions,
    #                 deletions=file.deletions,
    #                 changes=file.changes,
    #                 patch=file.patch,  # This contains the diff for the file
    #             )
    #         )

    #     pr: PR = PR(
    #         id=raw_pr.number,
    #         ticket_id=ticket.id,
    #         assignee_id=ticket.assignee_id,
    #         title=raw_pr.title,
    #         description=raw_pr.body if raw_pr.body is not None else "",
    #         files_changed=files_changed_with_diffs,
    #     )

    #     return pr

    def submit_code_review(self, generated_code_review: GeneratedCodeReview):
        print(generated_code_review.code_review)
        for comment in generated_code_review.code_review.comments:
            print("[REVIEWER] " + comment)
            if not "position" in comment:
                comment["position"] = 0

        print("[REVIEWER] Submitting code review...")
        self.gh_helper.submit_code_review(generated_code_review.code_review)
        print("[REVIEWER] Code review submitted!")

        trello_ticket_id = generated_code_review.code_review.pr.ticket_id
        if (generated_code_review.is_valid_code and generated_code_review.resolves_ticket):
            self.trello_helper.move_to_approved(ticket_id=trello_ticket_id)
        else:
            self.trello_helper.move_to_reviewed(ticket_id=trello_ticket_id)
        

    def proccess_pr(self):
        print("[REVIEWER] ---process_pr---")

        codebase = self.gh_helper.get_entire_codebase()

        # Get first open PR from GH that hasn't been approved yet
        pr = self.pr_backlog.pop(0)
                        
        # ticket_id = "660062487b43fbb4f1d5e8ea"
                
        # Todo: Fetch the Trello ticket that corresponds to this PR
        ticket = self.trello_helper.get_ticket(ticket_id=pr.ticket_id)
        
        # return
        # placeholder_ticket = Ticket(
        #     id="1",
        #     title="Improve with intructions to start",
        #     description="Our README should be more detailed on how to start the project.",
        #     assignee_id="0",
        #     status="backlog",
        # )


        # pr = self.simplify_pr(raw_pr=pr.raw_pr, ticket=ticket)

        generated_code_review = review_code(
            codebase=codebase, ticket=ticket, pr=pr
        )
        self.submit_code_review(generated_code_review=generated_code_review)

    def run(self):
        while True:
            self.refresh_pr_backlog()
            if len(self.pr_backlog) > 0:
                self.proccess_pr()
            time.sleep(10)
