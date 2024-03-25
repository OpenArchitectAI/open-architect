import dspy
import json
from src.lib.mistral_dspy import Mistral

mistral_key = json.load(open("creds.json"))["mistral"]

turbo = dspy.OpenAI(model="gpt-3.5-turbo-0125", max_tokens=4096)
gpt4 = dspy.OpenAI(model="gpt-4-0125-preview", max_tokens=4096)
mistral_7b = dspy.OllamaLocal(model="mistral")
mistral = Mistral(model="mistral-large-latest", api_key=mistral_key, max_tokens=4096)
