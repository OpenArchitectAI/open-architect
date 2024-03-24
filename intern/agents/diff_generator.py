import dspy
import json

from models import Codebase, Ticket


# Define the agent
class DiffGeneratorSignature(dspy.Signature):
    codebase = dspy.InputField()
    ticket = dspy.InputField()
    git_diff = dspy.OutputField(desc="Give ONLY the git diff")


class DiffGenerator(dspy.Module):
    def __init__(self):
        super().__init__()

        self.diff_generator = dspy.Predict(DiffGeneratorSignature)

    def forward(self, codebase: Codebase, ticket: Ticket):
        # Get the diff
        print("Generating diff")
        diff = self.diff_generator(
            codebase=json.dumps(codebase.model_dump()),
            ticket=json.dumps(ticket.model_dump()),
        )
        print("Diff generated")

        return diff.git_diff
