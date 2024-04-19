from models import Ticket, PR, CodeReview, Codebase
import dspy

class GeneratedCodeReview:
    is_valid_code: bool
    resolves_ticket: bool
    code_review: CodeReview

class ReviewerSignature(dspy.Signature):
    # Inputs
    # codebase: Codebase = dspy.InputField()
    ticket: Ticket = dspy.InputField()
    pr: PR = dspy.InputField()
    # Outputs
    is_valid_code: bool = dspy.OutputField(desc="Check if the code is actually valid.")
    resolves_ticket: bool = dspy.OutputField(
        desc="Does this code actually resolve the ticket? Is it changing the right files?"
    )
    code_review: CodeReview = dspy.OutputField(
        desc="If valid, provide a brief comment saying that it looks good. If not valid, provide comments for changes that are needed along with exact line numbers and/or start and end line number. If adding comments, make it different from the main body text."
    )


class ReviewerAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.code_review_generator = dspy.TypedPredictor(signature=ReviewerSignature)

    def forward(
        self, codebase: Codebase, pr: PR, ticket: Ticket
    ) -> GeneratedCodeReview:
        generated_review = self.code_review_generator(
            codebase=codebase, ticket=ticket, pr=pr
        )

        return generated_review