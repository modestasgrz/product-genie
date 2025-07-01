import sys
from pathlib import Path

# Add the parent directory of GrBackend to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from llm_service_domain.ollama import OllamaLLMService
from utils.config_dict import ConfigDict
from utils.logger import logger


def run_ollama_test():
    """
    Tests the OllamaLLMService by making a call with a specific prompt template.
    """
    try:
        # Load LLM configuration
        llm_config_path = (
            Path(__file__).parent.parent.parent / "configs/llm_config.json"
        )
        llm_config = ConfigDict(llm_config_path)

        # Load prompting template
        template_path = (
            Path(__file__).parent.parent.parent / "assets/prompting_template_v4.txt"
        )
        with open(template_path) as f:
            prompting_template = f.read().strip()

        # Initialize Ollama service
        # Use a default model, or get it from config if available
        ollama_model = llm_config.get(
            "ollama_model", "llama3.2"
        )  # Default to llama3.2 if not in config
        ollama_service = OllamaLLMService(config=llm_config, model=ollama_model)

        test_prompt = (
            "Camera spins around the bottle while flowers fly behind it"
            " that are interpolated linearly"
        )
        formatted_prompt = prompting_template % test_prompt

        logger.info(f"Attempting to call Ollama with model: {ollama_model}")
        logger.info(f"Sending formatted prompt:\n{formatted_prompt}\n")

        response = ollama_service.call(prompt=formatted_prompt)

        logger.info("\nOllama Response:")
        logger.info(response)
        logger.info("\nOllama test completed successfully!")

    except FileNotFoundError as e:
        logger.error(f"Error: Required file not found: {e}")
        logger.error(
            "Please ensure 'GrBackend/configs/llm_config.json' and "
            "'GrBackend/assets/prompting_template_v4.txt' exist."
        )
    except Exception as e:
        logger.error(f"\nOllama test failed: {e}")


if __name__ == "__main__":
    run_ollama_test()
