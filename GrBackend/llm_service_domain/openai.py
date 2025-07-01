from typing import Any

from openai import OpenAI

from llm_service_domain.llm_service import LLMService


# ! Deprecated - update to take config params from config.py (.env)
# TODO: UPDATE - this might not work
class OpenAILLMervice(LLMService):
    def __init__(self, config: dict[str, Any]):
        with open(config["open_ai_key_path"]) as f:
            api_key = f.read()

        self._model = config["open_ai_llm_model_type"]
        self._client = OpenAI(api_key=api_key)
        self._temperature = config["temperature"]

    def call(self, prompt: str, seed: int | None = None) -> str:
        if seed is None:
            seed = self._generate_seed()

        chat_response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            seed=seed,
            temperature=self._temperature,
        )

        return chat_response["choices"][0]["message"]["content"]  # type: ignore[no-any-return, index]
