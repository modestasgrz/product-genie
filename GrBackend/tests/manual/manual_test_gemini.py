import sys
from pathlib import Path

# Add the parent directory of GrBackend to the Python path
# This is necessary to import modules from GrBackend
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from llm_service_domain.gemini import GeminiLLMService
from src.config import GEMINI_API_KEY, GEMINI_MODEL


def run_gemini_test() -> None:
    """
    Tests the GeminiLLMService by making a simple call.
    """
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY is not set in GrBackend/src/config.py")
        print("Please set the GEMINI_API_KEY before running this test.")
        return

    print(f"Attempting to call Gemini with model: {GEMINI_MODEL}")
    try:
        gemini_service = GeminiLLMService()
        prompt = "Hello, Gemini! What is the capital of France?"
        print(f"Sending prompt: '{prompt}'")
        response = gemini_service.call(prompt)
        print("\nGemini Response:")
        print(response)
        print("\nGemini test completed successfully!")
    except Exception as e:
        print(f"\nGemini test failed: {e}")


if __name__ == "__main__":
    run_gemini_test()
