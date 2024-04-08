from typing import Dict, List
import dspy
import json

from src.agents.intern.generators.signatures import (
    NewFilesGeneratorSignature,
    RelevantFileSelectionSignature,
)
from src.models import Codebase, Ticket


SHOULD_RECORD_INPUT_OUTPUT = True


class CodeGenerator(dspy.Module):
    def __init__(self):
        super().__init__()

        self.relevant_file_selector = dspy.TypedChainOfThought(
            RelevantFileSelectionSignature
        )
        self.new_files_generator = dspy.TypedChainOfThought(NewFilesGeneratorSignature)

    def record_input_output(self, inputs: Dict, outputs: Dict):
        with open("tests/data/code_generator.json", "w") as f:
            json.dump(
                {
                    "inputs": inputs,
                    "outputs": outputs,
                },
                f,
            )

    def forward(self, codebase: Codebase, ticket: Ticket):
        relevant_files = self.relevant_file_selector(
            files_in_codebase=json.dumps(list(codebase.files.keys())),
            ticket=json.dumps(ticket.model_dump()),
        )

        subset_codebase = {
            file: codebase.files[file] for file in relevant_files.relevant_files
        }

        relevant_codebase = Codebase(files=subset_codebase)

        new_files = self.new_files_generator(
            relevant_codebase=json.dumps(relevant_codebase.model_dump()),
            ticket=json.dumps(ticket.model_dump()),
        )

        if SHOULD_RECORD_INPUT_OUTPUT:
            self.record_input_output(
                {
                    "codebase": codebase.model_dump(),
                    "ticket": ticket.model_dump(),
                },
                {
                    "relevant_files": relevant_files.relevant_files,
                    "new_files": new_files.new_files,
                    "explanations": new_files.explanations,
                },
            )

        return {
            "relevant_files": relevant_files.relevant_files,
            "new_files": new_files.new_files,
            "explanations": new_files.explanations,
        }
