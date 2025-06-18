from llm_service_domain.llm_service import LLMService
from utils.config import Config
import requests

class OllamaLLMService(LLMService):

    def __init__(self, config: Config | None = None):

        super().__init__(config)

        self._url = self._config["ollama_url"]
        self._temperature = self._config["temperature"]
        self._format = self._config["format"]


    def call(self, llm_prompt: str, model: str = "llama3.2") -> str:

        # if seed is None:
        #     seed = self._generate_seed()

        data = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": llm_prompt

                }
            ],
            "stream": False,
            "options" : {
                "temperature" : self._temperature
            },
            "format" : self._format
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(self._url, headers=headers, json=data)
        if response.status_code != 200:
            raise Exception(f"{response.status_code} - {str(response.json())}")
        return response.json()["message"]["content"]