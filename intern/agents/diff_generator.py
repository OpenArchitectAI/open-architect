import dspy


# Define the agent
class DiffGeneratorSignature(dspy.Signature):
    codebase = dspy.InputField()
    task_description = dspy.InputField()
    git_diff = dspy.OutputField()


class DiffGenerator(dspy.Module):
    def __init__(self):
        super().__init__()

        self.diff_generator = dspy.Predict(DiffGeneratorSignature)

    def forward(self, codebase, task_description):
        # Get the diff
        diff = self.diff_generator(codebase=codebase, task_description=task_description)

        return diff
