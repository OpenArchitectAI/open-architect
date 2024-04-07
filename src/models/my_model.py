# Example model file

class MyModel:
    def __init__(self):
        self.model_path = None

    def load_model(self, path):
        # Ensure to use complete paths
        self.model_path = path
        # Load the model from the path
        pass

# Ensure that when loading models, complete paths are used
model = MyModel()
model.load_model('/absolute/path/to/the/model')