import dspy

turbo = dspy.OpenAI(model="gpt-3.5-turbo-0125", max_tokens=4096)
gpt4 = dspy.OpenAI(model="gpt-4-0125-preview", max_tokens=4096)

mistral_7b = dspy.OllamaLocal(model="mistral")
