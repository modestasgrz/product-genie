import google.generativeai as genai

from src.config import GEMINI_API_KEY, GEMINI_MODEL
from utils.exceptions import GeminiAPIError


class GeminiLLMService:
    def __init__(self, model: str | None = None):
        genai.configure(api_key=GEMINI_API_KEY)

        self._model = model if model else GEMINI_MODEL
        self._client = genai.GenerativeModel(self._model)

        self.generation_config = genai.GenerationConfig(
            response_mime_type="application/json"
        )

    def call(self, prompt: str) -> str:
        try:
            response = self._client.generate_content(
                prompt, generation_config=self.generation_config
            )
            if response.text:
                return str(response.text)
            else:
                raise GeminiAPIError("No text content in Gemini response")

        except Exception as e:
            raise GeminiAPIError(f"Gemini API call failed: {str(e)}") from e
