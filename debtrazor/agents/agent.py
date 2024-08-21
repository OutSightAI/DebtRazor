from abc import abstractmethod


class Agent:
    def __init__(self, model, tools):
        """
        Initialize the Agent with a model and tools.

        :param model: The model that the agent will use.
        :param tools: The tools that the agent will use.
        """
        self.tools = tools  # Assign tools to the agent
        self.model = model  # Assign model to the agent

    @abstractmethod
    def __call__(**kwargs):
        """
        Abstract method to call the agent graph in the derived agent classes.

        :param kwargs: Arbitrary keyword arguments that can be passed to the method.
        """
        pass  # This method should be implemented in derived classes
