from pydantic import BaseModel


class Model(BaseModel):
    """
    A Pydantic model representing an entity with a single attribute 'name'.

    Attributes:
        name (str): The name of the entity.
    """

    name: str
