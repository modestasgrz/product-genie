"""
Product Video Service - Gradio Application

A refactored Gradio application for generating product videos using LLM analysis
and Blender rendering. This module follows component-based architecture with
proper separation of concerns.
"""

import json
from pathlib import Path
from typing import Any

import gradio as gr

from llm_service_domain.ollama import OllamaLLMService
from src.blender_renderer import BlenderRenderer
from src.config import (
    IS_DEBUG,
    PASSWORD,
    SERVICE_HOST,
    SERVICE_PORT,
    USERNAME,
)
from src.schemas import ShotCompositionParams
from utils.color_utils import ColorUtils
from utils.config_dict import ConfigDict
from utils.exceptions import JSONDecodeRetranslateError, ShotCompositionException
from utils.logger import logger


class LLM:
    """LLM service wrapper for shot composition analysis."""

    DEFAULT_MODEL = "qwen2.5:7b"
    DEFAULT_TRY_LIMIT = 3

    def __init__(self, config_path: Path | None = None, model: str | None = None):
        self.model = model or self.DEFAULT_MODEL
        self.try_limit = self.DEFAULT_TRY_LIMIT

        config_path = config_path or Path(__file__).parent / "configs/llm_config.json"
        self.service = OllamaLLMService(
            config=ConfigDict(config_path),
            model=self.model,
        )
        self.prompting_template = self._load_prompting_template()

    def _load_prompting_template(self, template_path: Path | None = None) -> str:
        """Load the prompting template."""
        if template_path is None:
            template_path = Path(__file__).parent / "assets/prompting_template_v4.txt"

        try:
            with open(template_path) as f:
                return f.read().strip()
        except FileNotFoundError as e:
            msg = f"Prompting template not found: {template_path}"
            logger.error(msg)
            raise FileNotFoundError(msg) from e

    def analyze_shot_composition(
        self, prompt: str, environment_color: str
    ) -> dict[str, Any]:
        """Analyze shot composition using LLM."""
        formatted_prompt = self.prompting_template % prompt

        for attempt in range(self.try_limit):
            try:
                llm_output = self.service.call(prompt=formatted_prompt)
                logger.debug(f"LLM Output (Attempt {attempt + 1}):\n{llm_output}")

                shot_params = ShotCompositionParams(**json.loads(llm_output))

                return self._create_composition_json(shot_params, environment_color)

            except (json.JSONDecodeError, JSONDecodeRetranslateError) as e:
                self._log_retry_message(e, llm_output, attempt)
            except Exception as e:
                self._log_retry_message(e, "Unknown error", attempt)

        raise ShotCompositionException(
            f"LLM Service retry limit ({self.try_limit}) exceeded. "
            "LLM might be working improperly."
        )

    def _log_retry_message(self, error: Exception, output: str, attempt: int) -> None:
        """Log retry message with error details."""
        remaining_tries = self.try_limit - attempt - 1
        logger.warning(f"""
        LLM Analysis Failed (Attempt {attempt + 1}/{self.try_limit}):
        Error: {error}
        Output: {output}
        Retries remaining: {remaining_tries}
        """)

    def _create_composition_json(
        self, params: ShotCompositionParams, env_color: str
    ) -> dict[str, Any]:
        """Create composition JSON from shot parameters."""
        return {
            "MOVEMENT": {
                "NAME": params.movement,
                "SPEED": params.movement_speed,
                "INTERPOLATION": params.movement_interpolation,
            },
            "ENVIRONEMENT": {"BACKGOUND_COLOR": ColorUtils.to_hex(env_color)},
            "VFX_SHOT": {
                "NAME": params.vfx_shot,
                "SPEED": params.vfx_shot_speed,
                "INTERPOLATION": params.vfx_shot_interpolation,
            },
        }


class MapsLoader:
    """Loader for movement and VFX maps."""

    def __init__(self) -> None:
        self.maps_data = self._load_maps()
        self.movement_actions = self.maps_data.get("MOVEMENT_ACTION_MAP", {})
        self.vfx_collections = self.maps_data.get("VFX_COLLECTION_MAP", {})

    def _load_maps(self) -> dict[str, Any]:
        """Load maps from JSON file."""
        maps_path = (
            Path(__file__).parent.parent
            / "ProductVideo/productvideo/properties/maps.json"
        )

        try:
            with open(maps_path) as f:
                return json.load(f)  # type: ignore[no-any-return]
        except FileNotFoundError:
            logger.warning(f"Maps file not found at {maps_path}")
            return {"MOVEMENT_ACTION_MAP": {}, "VFX_COLLECTION_MAP": {}}


class VideoProcessor:
    """Video processing component."""

    def __init__(self, llm: LLM, blender_renderer: BlenderRenderer):
        self.llm = llm
        self.blender_renderer = blender_renderer

    def generate_video(
        self, file_input: str, prompt: str, environment_color: str
    ) -> str:
        """
        Generate video from input parameters.

        Args:
            file_input: Uploaded GLB file
            prompt: Scene description prompt
            environment_color: Environment color

        Returns:
            Path to generated video file
        """
        if not file_input:
            raise ValueError("No file uploaded")

        if not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        try:
            # Analyze shot composition using LLM
            composition_data = self.llm.analyze_shot_composition(
                prompt, environment_color
            )

            # Process video rendering
            video_path = self.blender_renderer.render_video_from_glb(
                glb_file_path=file_input, json_data=composition_data
            )

            return video_path

        except Exception as e:
            logger.error(f"Video generation error: {e}")
            raise


class GradioInterface:
    """Gradio interface component."""

    def __init__(self, video_processor: VideoProcessor, maps_loader: MapsLoader):
        self.video_processor = video_processor
        self.maps_loader = maps_loader
        self.interface = self._create_interface()

    def _create_interface(self) -> gr.Blocks:
        """Create the Gradio interface."""
        with gr.Blocks(title="Product Video Service") as interface:
            with gr.Row():
                # Input Column
                with gr.Column():
                    file_input = gr.File(
                        label="Upload GLB File", elem_id="upload_glb", type="filepath"
                    )

                    prompt_input = gr.TextArea(
                        label="Describe the scene in detail",
                        placeholder=(
                            "Camera zooming into the bottle "
                            "while water sprinkles on the screen"
                        ),
                        lines=3,
                    )

                    environment_color = gr.ColorPicker(
                        label="Environment Color", value="rgba(255, 0, 0, 1)"
                    )

                    generate_button = gr.Button(
                        value="Generate Video", variant="primary"
                    )

                # Output Column
                with gr.Column():
                    output_video = gr.Video(label="Generated Video")

            # Event handlers
            generate_button.click(
                fn=self.video_processor.generate_video,
                inputs=[file_input, prompt_input, environment_color],
                outputs=output_video,
            )

        return interface  # type: ignore[no-any-return]

    def launch(self, **kwargs: dict[str, Any]) -> None:
        """Launch the Gradio interface."""
        self.interface.launch(**kwargs)  # type: ignore[arg-type]


class ProductVideoApp:
    """Main application class."""

    def __init__(self) -> None:
        self.llm = LLM()
        self.blender_renderer = BlenderRenderer()
        self.maps_loader = MapsLoader()
        self.video_processor = VideoProcessor(self.llm, self.blender_renderer)
        self.interface = GradioInterface(self.video_processor, self.maps_loader)

    def run(self) -> None:
        """Run the application."""
        launch_config = self._get_launch_config()
        self.interface.launch(**launch_config)

    def _get_launch_config(self) -> dict[str, Any]:
        """Get launch configuration based on environment."""

        base_config = {
            "debug": True,  # TODO: find out why it's needed
            "server_port": SERVICE_PORT,
            "server_name": SERVICE_HOST,
        }

        if IS_DEBUG:
            base_config["share"] = True
        else:
            base_config["auth"] = (USERNAME, PASSWORD)

        return base_config


def main() -> None:
    """Main entry point."""
    try:
        app = ProductVideoApp()
        app.run()
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise


if __name__ == "__main__":
    main()
