from typing import Dict, List
import dspy
import json

from models import Codebase, Ticket


class RelevantFileSelectionSignature(dspy.Signature):
    files_in_codebase = dspy.InputField()
    ticket = dspy.InputField()
    relevant_files: List[str] = dspy.OutputField(
        desc="Give the relevant files for you to observe to complete the ticket. They must be keys of the codebase dict."
    )


# Define the agent
class DiffGeneratorSignature(dspy.Signature):
    relevant_codebase = dspy.InputField()
    ticket = dspy.InputField()
    git_diff = dspy.OutputField(desc="Give ONLY the git diff")
    explanations = dspy.OutputField(desc="Give explanations for the diff generated")


class NewFilesGeneratorSignature(dspy.Signature):
    relevant_codebase = dspy.InputField()
    ticket = dspy.InputField()
    new_files: Dict[str, str] = dspy.OutputField(
        desc="Give the files that need to be update or created complete the ticket. The key is the path of the file and the value is the content of the file."
    )
    explanations = dspy.OutputField(
        desc="Give explanations for the new files generated."
    )


class DiffGenerator(dspy.Module):
    def __init__(self):
        super().__init__()

        self.diff_generator = dspy.ChainOfThought(DiffGeneratorSignature)
        self.relevant_file_selector = dspy.TypedPredictor(
            RelevantFileSelectionSignature
        )
        self.new_files_generator = dspy.TypedPredictor(NewFilesGeneratorSignature)

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

        print("Generating new files")
        new_files = self.new_files_generator(
            relevant_codebase=json.dumps(relevant_codebase.model_dump()),
            ticket=json.dumps(ticket.model_dump()),
        )
        print("New files generated")

        return new_files.new_files, new_files.explanations
