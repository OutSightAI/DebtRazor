from abc import abstractmethod


class Agent:
    def __init__(self, model, tools):
        self.tools = tools
        self.model = model

    @abstractmethod
    def __call__(**kwargs):
        """
        This method should call the agent graph in the derived agent classes
        """
