class Intern:
    def __init__(selfm, gh_helper, trello_helper):
        self.ticket_backlog = []
        self.pr_backlog = []
        self.gh_helper = gh_helper
        self.trello_helper = trello_helper

    def refresh_ticket_backlog(self):
        # Fetch from Trello
        # Append to backlog
        pass

    def refresh_pr_backlog(self):
        # Fetch from GitHub
        # Append to backlog
        pass

    def process_pr(self):
        # Get the first PR from the backlog
        # Process it (GH + Trello)
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