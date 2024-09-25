import os
import yaml
from langchain_openai import ChatOpenAI

# Define the directory paths for package, root, and configuration files
PACKAGE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(PACKAGE_DIR)
CONFIG_DIR = os.path.join(ROOT_DIR, "configs")


def get_llm(model_params, llm_yaml_path=None):
    """
    Retrieves a language model (LLM) based on the provided model parameters.

    Args:
        model_params (object): An object containing model parameters.
                               The object should have a 'name' attribute.
        llm_yaml_path (str, optional): The path to the llm.yaml configuration file.
                                       Defaults to None.

    Returns:
        ChatOpenAI: An instance of the ChatOpenAI class configured with the specified model.

    Raises:
        ValueError: If the LLM name is not found in the llm.yaml configuration file.
        ValueError: If the type specified in the llm.yaml is not recognized.
        ValueError: If the API specified in the llm.yaml is not recognized.
    """
    # Convert model parameters to a dictionary
    model_params = model_params.__dict__
    name = model_params["name"]

    # Load the LLM configuration from the llm.yaml file
    if llm_yaml_path is None:
        llm_yaml_path = os.path.join(CONFIG_DIR, "llm.yaml")
    
    with open(llm_yaml_path, "r") as fp:
        llm_yaml = yaml.safe_load(fp)

    try:
        # Retrieve the parameters for the specified LLM name
        llm_yaml_params = llm_yaml[name]
    except KeyError:
        # Raise an error if the LLM name is not found in the configuration file
        raise ValueError(f"LLM name {name} not found in llm.yaml")

    # Only supports OpenAI for now and only completion for now
    # TODO: Other types and non OpenAI models
    if llm_yaml_params["api"] == "openai":
        if llm_yaml_params["type"] == "completion":
            # Return an instance of ChatOpenAI with the specified model name and temperature
            return ChatOpenAI(model=name, temperature=0)
        else:
            # Raise an error if the type is not recognized
            raise ValueError(f'type {llm_yaml_params["type"]} not recognized')
    else:
        # Raise an error if the API is not recognized
        raise ValueError(f'API {llm_yaml_params["api"]} not recognized')
