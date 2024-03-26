import dspy

from src.agents.reviewer.generators.code_review_generator import (
    GeneratedCodeReview,
    ReviewerAgent,
)

from src.language_models import gpt4
from src.models import Codebase, Ticket, PR


def fix_code(codebase: Codebase, ticket: Ticket, pr: PR):
    # Note this function will most likely be implemented by the intern
    # This function is responsible for fixing the code
    # It should take the codebase, the ticket and the PR
    # It should update the codebase that is passed in and return that codebase
    updatedCodebase = codebase
    return updatedCodebase


def review_code(codebase: Codebase, ticket: Ticket, pr: PR) -> GeneratedCodeReview:
    # This function is responsible for reviewing the code
    # It should take each of the PR comments, the associated code chunks
    # It should update comment on the PR and either approve or request changes
    dspy.configure(lm=gpt4)

    reviewer_agent = ReviewerAgent()

    code_review = reviewer_agent(codebase=codebase, ticket=ticket, pr=pr)

    return code_review
