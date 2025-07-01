import random
from abc import ABC, abstractmethod

from utils.config_dict import ConfigDict


# ! Deprecated - update to take config params from config.py (.env)
class LLMService(ABC):
    @abstractmethod
    def __init__(self, config: ConfigDict | None = None) -> None:
        self._config = (
            config if config is not None else ConfigDict("configs/llm_config.json")
        )

    @abstractmethod
    def call(self, prompt: str, seed: int | None) -> str:
        pass

    def _generate_seed(self) -> int:
        return int(random.random() * 1000000000000)
