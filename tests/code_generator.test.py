# Import path above
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.agents.intern.generators.code_generator import CodeGenerator
from src.models import Codebase, Ticket
from src.language_models import gpt4
import dspy
import json
from dotenv import load_dotenv


if __name__ == "__main__":
    load_dotenv()

    dspy.configure(lm=gpt4)

    code_generator = CodeGenerator()

    # Import the ticket and codease from a json file in data/code_generator.json
    with open("tests/data/code_generator.json", "r") as f:
        data = json.load(f)

        codebase = Codebase(**data["inputs"]["codebase"])
        ticket = Ticket(**data["inputs"]["ticket"])

    res = code_generator(codebase, ticket)
    print(res)
