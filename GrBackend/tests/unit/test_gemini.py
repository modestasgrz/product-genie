import unittest
from unittest.mock import MagicMock, patch

from llm_service_domain.gemini import GeminiLLMService
from utils.exceptions import GeminiAPIError


# TODO: Fix this test, when unit testing will be a thing here
class TestGeminiLLMService(unittest.TestCase):
    @patch("src.config.GEMINI_API_KEY", "mock_api_key")
    @patch("src.config.GEMINI_MODEL", "mock_model")
    @patch("google.generativeai.GenerativeModel")
    def test_call(self, mock_generative_model: MagicMock) -> None:
        # Setup mock for successful response
        mock_instance = MagicMock()
        mock_generative_model.return_value = mock_instance
        mock_instance.generate_content.return_value.text = "Mocked Gemini Response"

        service = GeminiLLMService()
        prompt = "Test prompt"
        response = service.call(prompt)

        mock_generative_model.assert_called_once_with("mock_model")
        mock_instance.generate_content.assert_called_once_with(prompt)
        self.assertEqual(response, "Mocked Gemini Response")

        # Test case: Empty response text
        mock_instance.generate_content.return_value.text = ""
        with self.assertRaises(GeminiAPIError) as cm:
            service.call(prompt)
        self.assertIn("No text content in Gemini response", str(cm.exception))

        # Test case: API call raises an exception
        mock_instance.generate_content.side_effect = Exception("API Error")
        with self.assertRaises(GeminiAPIError) as cm:
            service.call(prompt)
        self.assertIn("Gemini API call failed: API Error", str(cm.exception))
