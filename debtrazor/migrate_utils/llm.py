import os
import yaml
from langchain_openai import ChatOpenAI

PACKAGE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(PACKAGE_DIR)
CONFIG_DIR = os.path.join(ROOT_DIR, "configs")


def get_llm(model_params):
    model_params = model_params.__dict__
    name = model_params["name"]

    llm_yaml_path = os.path.join(CONFIG_DIR, "llm.yaml")
    with open(llm_yaml_path, "r") as fp:
        llm_yaml = yaml.safe_load(fp)
    try:
        llm_yaml_params = llm_yaml[name]
    except KeyError:
        raise ValueError(f"LLM name {name} not found in llm.yaml")

    # Only supports OpenAI for now and only completion for now
    # TODO: Other types and non OpenAI models
    if llm_yaml_params["api"] == "openai":
        if llm_yaml_params["type"] == "completion":
            return ChatOpenAI(model=name, temperature=0)
        else:
            raise ValueError(f'type {llm_yaml_params["type"]} not recognized')
    else:
        raise ValueError(f'API {llm_yaml_params["api"]} not recognized')
