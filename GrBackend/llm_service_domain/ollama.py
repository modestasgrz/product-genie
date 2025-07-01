import requests

from llm_service_domain.llm_service import LLMService
from utils.config_dict import ConfigDict


# ! Will be Deprecated - update to take config params from config.py (.env)
class OllamaLLMService(LLMService):
    def __init__(self, config: ConfigDict | None = None, model: str = "llama3.2"):
        super().__init__(config)

        self._url = self._config["ollama_url"]
        self._temperature = self._config["temperature"]
        self._format = self._config["format"]
        self._model = model

    def call(self, prompt: str, seed: int | None = None) -> str:
        # if seed is None:
        #     seed = self._generate_seed()

        options = {"temperature": self._temperature}
        if seed is not None:
            options["seed"] = seed

        data = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": options,
            "format": self._format,
        }

        headers = {"Content-Type": "application/json"}

        response = requests.post(self._url, headers=headers, json=data)
        if response.status_code != 200:
            raise Exception(f"{response.status_code} - {str(response.json())}")
        return response.json()["message"]["content"]  # type: ignore[no-any-return]
