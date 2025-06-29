from mistralai import Mistral

from llm_service_domain.llm_service import LLMService
from utils.config_dict import ConfigDict


# TODO: UPDATE - there might be issues with this implementation.
class MistralAILLMService(LLMService):
    def __init__(self, config: ConfigDict):
        super().__init__(config)
        with open(config["mistral_ai_key_path"]) as f:
            api_key = f.read()

        self._model = config["mistral_ai_llm_model_type"]
        self._client = Mistral(api_key=api_key)
        self._temperature = config["temperature"]

    def call(self, prompt: str, seed: int | None = None) -> str:
        if seed is None:
            seed = self._generate_seed()

        chat_response = self._client.chat.complete(
            model=self._model,
            messages=[  # type: ignore[arg-type]
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            random_seed=seed,
            temperature=self._temperature,
        )
        return chat_response.choices[0].message.content  # type: ignore[return-value]
