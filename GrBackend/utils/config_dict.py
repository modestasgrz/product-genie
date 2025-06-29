import json
from pathlib import Path


class ConfigDict(dict):
    def __init__(self, config_path: str | Path) -> None:
        super().__init__()
        with open(config_path) as f:
            data = json.loads(f.read())

        self.update(data)
