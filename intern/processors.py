def better_code_change(previous_code_change, pr, comments):
    # This function will be called from Intern.process_pr
    # It will take the previous code_change, the pr and the comments
    # and will return a new code_change
    # The previous code_change will be the last code_change that was pushed to the PR
    # The pr will be the PR that is being processed
    # The comments will be the comments that were made on the PR since the last code_change
    # The function will return a new code_change that will be pushed to the PR
    return "new_code_change"

def code_change(ticket_scope, code_base):
    # This function will be called from Intern.process_ticket
    # It will take the ticket_scope and the code_base
    # and will return a new code_change

    return "code_change" 