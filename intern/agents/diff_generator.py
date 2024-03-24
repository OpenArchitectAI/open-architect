from typing import List
import dspy
import json

from models import Codebase, Ticket


# Define the agent
class DiffGeneratorSignature(dspy.Signature):
    relevant_codebase = dspy.InputField()
    ticket = dspy.InputField()
    git_diff = dspy.OutputField(desc="Give ONLY the git diff")
    explanations = dspy.OutputField(desc="Give explanations for the diff generated")


class RelevantFileSelectionSignature(dspy.Signature):
    files_in_codebase = dspy.InputField()
    ticket = dspy.InputField()
    relevant_files: List[str] = dspy.OutputField(
        desc="Give the relevant files for you to observe to complete the ticket. They must be keys of the codebase dict."
    )


class DiffGenerator(dspy.Module):
    def __init__(self):
        super().__init__()

        self.diff_generator = dspy.ChainOfThought(DiffGeneratorSignature)
        self.relevant_file_selector = dspy.TypedPredictor(
            RelevantFileSelectionSignature
        )

    def forward(self, codebase: Codebase, ticket: Ticket):
        print("First step: Selecting relevant files")
        relevant_files = self.relevant_file_selector(
            files_in_codebase=json.dumps(list(codebase.files.keys())),
            ticket=json.dumps(ticket.model_dump()),
        )

        print("Relevant files selected:", relevant_files.relevant_files)
        subset_codebase = {
            file: codebase.files[file] for file in relevant_files.relevant_files
        }
        print("Subset codebase created")

        relevant_codebase = Codebase(files=subset_codebase)

        print("Generating diff")
        diff = self.diff_generator(
            relevant_codebase=json.dumps(relevant_codebase.model_dump()),
            ticket=json.dumps(ticket.model_dump()),
        )
        print("Diff generated")

        return diff.git_diff, diff.explanations
