from abc import ABC, abstractmethod
import random

from utils.config import Config

class LLMService(ABC):

    @abstractmethod
    def __init__(self, config: Config | None = None):

        self._config = config if config is not None else Config("configs/llm_config.json")



    @abstractmethod
    def call(self, prompt, seed):
        pass


    def _generate_seed(self) -> int:
        return int(random.random() * 1000000000000)