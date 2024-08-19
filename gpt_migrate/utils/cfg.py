"""
Helper class to convert a config dict to an object
whose previous keys we can access with . notation
"""

import os
from typing import List

path_cfg_keys: List[str] = []


class Config:
    def __init__(self, data):
        for name, value in data.items():
            if name in path_cfg_keys and value is not None:
                # convert path to absolute an path
                abs_path = os.path.abspath(value)
                setattr(self, name, abs_path)
            else:
                setattr(self, name, self._wrap(value))

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self._wrap(v) for v in value])
        else:
            return Config(value) if isinstance(value, dict) else value

    def __str__(self):
        # Recursively print out config
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
