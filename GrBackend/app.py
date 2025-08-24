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

from google_sheets_domain.gsheets import GSheetsService
from llm_service_domain.gemini import GeminiLLMService
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
from utils.exceptions import JSONDecodeRetranslateError, ShotCompositionException
from utils.logger import logger


class LLM:
    """LLM service wrapper for shot composition analysis."""

    DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
    DEFAULT_OLLAMA_MODEL = "qwen2.5:7b"
    DEFAULT_TRY_LIMIT = 3

    def __init__(self) -> None:
        self.try_limit = self.DEFAULT_TRY_LIMIT

        self.service = GeminiLLMService()
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
                logger.info(f"User's entered prompt: {prompt}")
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
                "ROTATION_DIRECTION": "CLOCKWISE",
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
        maps_path = Path(__file__).parent / "maps.json"

        try:
            with open(maps_path) as f:
                return json.load(f)  # type: ignore[no-any-return]
        except FileNotFoundError:
            logger.warning(f"Maps file not found at {maps_path}")
            return {"MOVEMENT_ACTION_MAP": {}, "VFX_COLLECTION_MAP": {}}


class VideoProcessor:
    """Video processing component."""

    def __init__(
        self,
        llm: LLM,
        blender_renderer: BlenderRenderer,
        gsheets_service: GSheetsService,
        maps_data: dict[str, Any],
    ):
        with open("assets/assets.json") as f:
            self.assets = json.load(f)
        self.llm = llm
        self.blender_renderer = blender_renderer
        self.maps_data = maps_data
        self.gsheets_service = gsheets_service

    def generate_video_from_prompt(
        self,
        file_input: str,
        prompt: str,
        environment_color: str,
    ) -> str:
        """
        Generate video from input parameters.

        Args:
            file_input: Uploaded GLB file
            prompt: Scene description prompt
            environment_color: Environment color
            rotation_direction: Clockwise or Counter-Clockwise rotation

        Returns:
            Path to generated video file
        """
        # TODO: later with rotations implemeted, remove try-except logic and pass
        # TODO: rotation_direction to llm.analyze_shot_composition
        # TODO: and add rotation_direction to arguments
        rotation_direction = ""
        try:
            rotation_direction = self.maps_data["ROTATION_DIRECTION_MAP"][
                rotation_direction
            ]
            logger.info(f"Rotation direction selected: {rotation_direction}")
        except Exception:
            pass
        if not file_input:
            raise ValueError("No file uploaded")

        if not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        try:
            # Analyze shot composition using LLM
            self.gsheets_service.store_prompt_in_sheet(prompt)
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

    def generate_video_from_args(
        self,
        file_input: str,
        movement_name: str,
        vfx_name: str,
        environment_color: str,
    ) -> str:
        """
        Generate video from input parameters.

        Args:
            file_input: Uploaded GLB file
            prompt: Scene description prompt
            environment_color: Environment color
            rotation_direction: Clockwise or Counter-Clockwise rotation

        Returns:
            Path to generated video file
        """
        if not file_input:
            raise ValueError("No file uploaded")

        movement_name = self.assets.get("Movement").get(movement_name[0].get("caption"))
        vfx_name = self.assets.get("VFX").get(vfx_name[0].get("caption"))
        logger.debug("---Input Args---")
        logger.debug(file_input)
        logger.debug(movement_name)
        logger.debug(vfx_name)
        logger.debug(environment_color)
        logger.debug("----------------")

        try:
            composition_data = {
                "MOVEMENT": {
                    "NAME": movement_name,
                    "SPEED": 1.2,
                    "INTERPOLATION": "None",
                    "ROTATION_DIRECTION": "CLOCKWISE",
                },
                "ENVIRONEMENT": {
                    "BACKGOUND_COLOR": ColorUtils.to_hex(environment_color)
                },
                "VFX_SHOT": {
                    "NAME": vfx_name,
                    "SPEED": 1.0,
                    "INTERPOLATION": "None",
                },
            }

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

    def __init__(self, video_processor: VideoProcessor):
        """
        Initializes the Gradio interface.
        Args:
            video_processor: An object with a 'generate_video' method.
        """

        self.video_processor = video_processor
        self.assets = video_processor.assets
        self.interface = self._create_interface()

    def _create_interface(self) -> gr.Blocks:
        """
        Creates the full Gradio interface with a professional and aligned layout.
        """
        # --- CSS for custom styling and alignment ---
        custom_css = """
        .gradio-container { background-color: #1a1a1a; color: white; }
        #model_3d_preview, #rendered_result { height: 400px !important; }
        #settings_row { align-items: stretch; }
        #settings_row > div { display: flex !important; }
        #generate_button { flex-grow: 1; }
        #env_color_picker button { margin-left: 10px; width: 150px; }
        /* Style for the gallery items */
        .gallery-item {
            border: 2px solid transparent;
            border-radius: 8px;
            transition: border-color 0.2s ease-in-out;
        }
        /* Style for selected gallery items */
        .gallery-item.selected {
            border: 2px solid #ef4444; /* Red border for selected items */
        }
        """

        # --- Define the presets and create placeholder image data ---
        animation_presets = self.assets.get("Movement").keys()
        vfx_presets = self.assets.get("VFX").keys()

        # Generate placeholder images for the gallery
        animation_gallery_data = [
            (
                f"https://placehold.co/128x128/2d3748/ffffff?text={p.replace(' ', '%0A')}",  # noqa: E501
                p,
            )
            for p in animation_presets
        ]
        vfx_gallery_data = [
            (
                f"https://placehold.co/128x128/2d3748/ffffff?text={p.replace(' ', '%0A')}",  # noqa: E501
                p,
            )
            for p in vfx_presets
        ]

        # --- Build the Gradio Interface ---
        with gr.Blocks(
            title="3D Animation Studio",
            theme=gr.themes.Default(
                primary_hue="red", secondary_hue="neutral", neutral_hue="slate"
            ),
            css=custom_css,
        ) as interface:
            gr.Markdown(
                "# 3D Animation Studio "
                "<span style='color: #ff4d4d; font-size: 12px;'>Beta</span>"
            )

            # --- State variables to store selected presets ---
            selected_animations = gr.State([])
            selected_vfx = gr.State([])

            with gr.Row():
                # --- Left Column: 3D Model Preview and Upload ---
                with gr.Column():
                    gr.Markdown("### 3D Model Preview")
                    file_input = gr.Model3D(
                        label="3D Model Preview",
                        elem_id="model_3d_preview",
                        camera_position=(0, 0, 3),
                    )

                # --- Right Column: Rendered Result ---
                with gr.Column():
                    gr.Markdown("### Rendered Result")
                    output_video = gr.Video(
                        label="Generated Video",
                        elem_id="rendered_result",
                    )

            # --- Middle Row: Controls ---
            with gr.Row(elem_id="settings_row"):
                environment_color = gr.ColorPicker(
                    label="Environment Color",
                    value="#4c82f7",
                    elem_id="env_color_picker",
                )
                generate_button = gr.Button(
                    "Generate Video",
                    variant="primary",
                    elem_id="generate_button",
                    scale=2,
                )

            # --- Bottom Rows: Presets ---
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Animation Presets")
                    animation_gallery = gr.Gallery(
                        label="Animation Presets",
                        value=animation_gallery_data,
                        columns=5,
                        height="auto",
                        allow_preview=False,
                    )
                with gr.Column():
                    gr.Markdown("### VFX Presets")
                    vfx_gallery = gr.Gallery(
                        label="VFX Presets",
                        value=vfx_gallery_data,
                        columns=5,
                        height="auto",
                        allow_preview=False,
                    )

            # --- Event Handlers ---

            def handle_selection(current_selection: list[str], evt: gr.SelectData):
                """Generic handler to update the list of selected items."""
                caption = evt.value
                if evt.selected:
                    current_selection.append(caption)
                else:
                    if caption in current_selection:
                        current_selection.remove(caption)
                return current_selection

            animation_gallery.select(
                fn=handle_selection,
                inputs=[selected_animations],
                outputs=[selected_animations],
            )

            vfx_gallery.select(
                fn=handle_selection,
                inputs=[selected_vfx],
                outputs=[selected_vfx],
            )

            generate_button.click(
                fn=self.video_processor.generate_video_from_args,
                inputs=[
                    file_input,
                    selected_animations,
                    selected_vfx,
                    environment_color,
                ],
                outputs=output_video,
            )

        return interface  # type: ignore[no-any-return]

    def launch(self, **kwargs: dict[str, Any]) -> None:
        """Launch the Gradio interface."""
        self.interface.launch(**kwargs)  # type: ignore[arg-type]


class ProductVideoApp:
    """Main application class."""

    def __init__(self) -> None:
        maps_loader = MapsLoader()
        llm = LLM()
        blender_renderer = BlenderRenderer()
        gsheets_service = GSheetsService()
        video_processor = VideoProcessor(
            llm, blender_renderer, gsheets_service, maps_loader.maps_data
        )
        self.interface = GradioInterface(video_processor)

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
