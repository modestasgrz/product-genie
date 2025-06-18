from llm_service_domain.llm_service import LLMService
from mistralai import Mistral
from typing import Dict, Any

# TODO: UPDATE
class MistralAILLMService(LLMService):

    def __init__(self, config: Dict[str, Any]):

        super().__init__(config)
        with open(config["mistral_ai_key_path"]) as f:
            api_key=f.read()

        self._model = config["mistral_ai_llm_model_type"]
        self._client = Mistral(api_key=api_key)
        self._temperature = config["temperature"]


    def call(self, llm_prompt: str, seed: int = None) -> str:

        if seed is None:
            seed = self._generate_seed()

        chat_response = self._client.chat.complete(
            model= self._model,
            messages = [
                {
                    "role": "user",
                    "content": llm_prompt,
                },
            ],
            random_seed=seed,
            temperature=self._temperature
        )
        return chat_response.choices[0].message.content