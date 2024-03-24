from intern.processors import better_code_change, generate_code_change
from helpers.gh_helper import GHHelper
from helpers.trello_helper import TrelloHelper
import time
from typing import List

from models import Ticket


class Intern:
    def __init__(self, name, gh_api_token, gh_repo, trello_helper):
        self.name = name
        self.ticket_backlog: List[Ticket] = []
        self.pr_backlog = []
        self.gh_helper: GHHelper = GHHelper(gh_api_token, gh_repo)
        self.trello_helper: TrelloHelper = TrelloHelper()

    def refresh_ticket_backlog(self):
        next_tickets = [
            t
            for t in self.trello_helper.get_backlog_tickets()
            if t not in self.ticket_backlog and t.assignee == self.name
        ]
        self.ticket_backlog.extend(next_tickets)

    def refresh_pr_backlog(self):
        next_prs = [
            pr
            for pr in self.gh_helper.list_open_prs()
            if pr not in self.pr_backlog and pr.assignee == self.name
        ]
        self.pr_backlog.extend(next_prs)

    def process_pr(self):
        pr = self.pr_backlog.pop(0)
        self.trello_helper.move_to_wip(pr)
        comment = self.gh_helper.get_comments(pr)
        # Do some processing with LLMs, create a new code_change
        code_change = generate_code_change("", comment)
        self.gh_helper.push_changes(code_change)
        self.trello_helper.move_to_waiting_for_review(pr)
        pass

    def process_ticket(self):
        # Get the first ticket from the backlog
        # Process it (Trello + GH)

        ticket = self.ticket_backlog.pop(0)

        # Move ticket to WIP
        self.trello_helper.move_to_wip(ticket)

        # There should not be some PRs already assigned to this ticket (for now)
        # Call an agent to create a PR
        code_change = generate_code_change(ticket, self.gh_helper.get_entire_codebase())

        print("Pushing changes to a PR")
        # Push the changes to the PR
        self.gh_helper.push_changes(ticket.title, code_change)

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
