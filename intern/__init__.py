from intern.processors import better_code_change, generate_code_change
from random import choice
import time
from typing import List
from models import Ticket

from gh_helper import GHHelper
from trello_helper import TrelloHelper


class Intern:
    def __init__(self, name, gh_helper: GHHelper, trello_helper: TrelloHelper):
        self.name = name
        self.id = choice(trello_helper.get_labels())
        self.ticket_backlog: List[Ticket] = []
        self.pr_backlog = []
        self.gh_helper = gh_helper
        self.trello_helper = trello_helper
        print(f"Hey! I'm {self.name}, excited to start working!")

    def refresh_ticket_backlog(self):
        next_tickets = [
            t
            for t in self.trello_helper.get_backlog_tickets()
            if t not in self.ticket_backlog and t.assignee_id == self.id
        ]
        self.ticket_backlog.extend(next_tickets)

    def refresh_pr_backlog(self):
        next_prs = [
            pr
            for pr in self.gh_helper.list_open_prs()
            if pr not in self.pr_backlog and pr.assignee_id == self.id
        ]
        self.pr_backlog.extend(next_prs)

    def process_pr(self):
        pr = self.pr_backlog.pop(0)
        self.trello_helper.move_to_wip(pr.ticket_id)
        comment = self.gh_helper.get_comments(pr)
        # Do some processing with LLMs, create a new code_change
        code_change = generate_code_change("", comment)
        self.gh_helper.push_changes(code_change, pr.ticket_id, pr.assignee_id)
        self.trello_helper.move_to_waiting_for_review(pr.ticket_id)
        pass

    def process_ticket(self):
        # Get the first ticket from the backlog
        # Process it (Trello + GH)

        ticket = self.ticket_backlog.pop(0)

        # Move ticket to WIP
        self.trello_helper.move_to_wip(ticket.id)

        # There should not be some PRs already assigned to this ticket (for now)
        # Call an agent to create a PR
        new_files, body = generate_code_change(
            ticket, self.gh_helper.get_entire_codebase()
        )

        print("Pushing changes to a PR")
        # Push the changes to the PR
        branch_name = f"{ticket.id}_{ticket.title.lower().replace(' ', '_')}"
        self.gh_helper.push_changes(
            branch_name=branch_name,
            pr_title=ticket.title,
            pr_body=body,
            new_files=new_files,
            ticket_id=ticket.id,
            author_id=ticket.assignee_id,
        )

        print("PR Created")

    def run(self):
        # Two threads are created running in an infinite loop
        # The first one listens to refresh commands and refreshes the backlogs
        # The second one consumes the backlogs and processes the tickets and PRs

        # Different implementation than comment above but same idea
        while True:
            if self.pr_backlog:
                self.process_pr()
            elif self.ticket_backlog:
                self.process_ticket()
            else:
                self.refresh_ticket_backlog()
                self.refresh_pr_backlog()
                time.sleep(30)
