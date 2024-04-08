import dspy
from typing import Dict, List


class RelevantFileSelectionSignature(dspy.Signature):
    files_in_codebase = dspy.InputField()
    ticket = dspy.InputField()
    relevant_files: List[str] = dspy.OutputField(
        desc="Give the relevant files for you to observe to complete the ticket. They must be keys of the files_in_codebase dict."
    )


# Define the agent
class NewFilesGeneratorSignature(dspy.Signature):
    relevant_codebase = dspy.InputField()
    ticket = dspy.InputField()
    new_files: Dict[str, str] = dspy.OutputField(
        desc="Generate the entire files that need to be update or created complete the ticket, with all of their content post update. The key is the path of the file and the value is the content of the file."
    )
    explanations = dspy.OutputField(
        desc="Give explanations for the new files generated. Use Markdown to format the text."
    )
