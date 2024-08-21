"""
Helper class to convert a config dict to an object
whose previous keys we can access with . notation
"""

import os
from typing import List

path_cfg_keys: List[str] = []


class Config:
    def __init__(self, data):
        """
        Initialize the Config object by converting a dictionary into an object
        with attributes accessible via dot notation.

        Args:
            data (dict): The configuration dictionary to be converted.
        """
        for name, value in data.items():
            if name in path_cfg_keys and value is not None:
                # Convert path to an absolute path
                abs_path = os.path.abspath(value)
                setattr(self, name, abs_path)
            else:
                setattr(self, name, self._wrap(value))

    def _wrap(self, value):
        """
        Recursively wrap dictionary values into Config objects and handle
        collections by wrapping their elements.

        Args:
            value: The value to be wrapped. It can be a dict, list, tuple, set, frozenset, or any other type.

        Returns:
            The wrapped value. If the value is a dict, it returns a Config object.
            If the value is a collection, it returns the same type of collection with wrapped elements.
            Otherwise, it returns the value itself.
        """
        if isinstance(value, (tuple, list, set, frozenset)):
            # Recursively wrap each element in the collection
            return type(value)([self._wrap(v) for v in value])
        else:
            # Wrap dicts into Config objects, leave other types as is
            return Config(value) if isinstance(value, dict) else value

    def __str__(self):
        """
        Recursively convert the Config object into a string representation.

        Returns:
            str: The string representation of the Config object.
        """

        def _str(data, indent=0):
            if isinstance(data, Config):
                data = data.__dict__
            out = ""
            for name, value in data.items():
                if isinstance(value, Config):
                    out += "  " * indent + f"{name}:\n"
                    out += _str(value, indent=indent + 1)
                else:
                    out += "  " * indent + f"{name}: {value}\n"
            return out

        return _str(self)
