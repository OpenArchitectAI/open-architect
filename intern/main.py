from processors import better_code_change, code_change

class Intern:
    def __init__(selfm, name, gh_helper, trello_helper):
        self.name = name
        self.ticket_backlog = []
        self.pr_backlog = []
        self.gh_helper = gh_helper
        self.trello_helper = trello_helper

    def refresh_ticket_backlog(self):
        next_tickets = [t for t in self.trello_helper.get_backlog_tickets() if t not in self.ticket_backlog and t.assignee == self.name]
        self.ticket_backlog.extend(next_tickets)

    def refresh_pr_backlog(self):
        next_prs = [pr for pr in self.gh_helper.list_open_prs() if pr not in self.pr_backlog and pr.assignee == self.name]
        self.pr_backlog.extend(next_prs)

    def process_pr(self):
        pr = self.pr_backlog.pop(0)
        self.trello_helper.move_to_wip(pr)
        comment = self.gh_helper.get_comments(pr)
        # Do some processing with LLMs, create a new code_change
        code_change = code_change("", comment)
        self.gh_helper.push_changes(code_change)
        self.trello_helper.move_to_waiting_for_review(pr)
        pass

    def process_ticket(self):
        # Get the first ticket from the backlog
        # Process it (Trello + GH)
        pass

    def run(self):
        # Two threads are created running in an infinite loop
        # The first one listens to refresh commands and refreshes the backlogs
        # The second one consumes the backlogs and processes the tickets and PRs
        pass