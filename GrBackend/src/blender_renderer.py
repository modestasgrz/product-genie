"""
API Process Module

This module handles video rendering processes using Blender.
It provides functionality to execute Blender commands and render images/videos
from GLB files and JSON configurations.
"""

import random
import string
import subprocess
from collections.abc import Generator
from pathlib import Path
from typing import Any

from src.config import (
    BLEND_BASE_FILE,
    BLENDER_APP,
    BLENDER_SCRIPT_FILE,
)
from src.file_handler import FileHandler
from utils.exceptions import BlenderProcessError
from utils.logger import logger

# Constants
TEMP_DIRECTORY = Path(__file__).parent.parent / "temp_dir"
UNIQUE_FILENAME_LENGTH = 12
BLENDER_FUNCTION_NAME = "process"


class BlenderRenderer:
    """
    Handles Blender rendering operations.

    This class encapsulates all Blender-related functionality including
    command execution and file processing.
    """

    def __init__(self) -> None:
        """Initialize the BlenderRenderer with environment validation."""
        self._ensure_temp_directory()

    def _ensure_temp_directory(self) -> None:
        """Ensure the temporary directory exists."""
        try:
            TEMP_DIRECTORY.mkdir(parents=True, exist_ok=True)
            logger.info(f"Temporary directory ensured: {TEMP_DIRECTORY}")
        except OSError as e:
            logger.error(f"Failed to create temporary directory: {e}")
            raise BlenderProcessError(f"Cannot create temporary directory: {e}") from e

    def _execute_command(self, command: list[str]) -> Generator[str, None, None]:
        """
        Execute a command and yield stdout lines with real-time output display.

        Args:
            command: List of command arguments to execute.

        Yields:
            str: Lines from stdout.

        Raises:
            BlenderProcessError: If command execution fails.
        """
        # Log command for visibility
        command_str = " ".join(command)
        logger.info("🎬 Starting Blender process...")
        logger.debug(f"Command: {command_str}")

        try:
            with subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
            ) as process:
                # Yield stdout lines as they come with real-time display
                if process.stdout:
                    for line in iter(process.stdout.readline, ""):
                        line = line.rstrip()
                        if line:  # Only process non-empty lines
                            # Display output in real-time with logging
                            logger.info(f"Blender: {line}")
                            yield line

                # Wait for process to complete
                return_code = process.wait()

                if return_code == 0:
                    logger.info("✅ Blender process completed successfully")
                else:
                    error_msg = f"Blender process failed with return code {return_code}"
                    logger.error(f"❌ {error_msg}")
                    raise BlenderProcessError(error_msg, return_code)

        except FileNotFoundError as e:
            error_msg = f"Blender executable not found: {command[0]}"
            logger.error(f"❌ {error_msg}")
            raise BlenderProcessError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error executing Blender command: {e}"
            logger.error(f"❌ {error_msg}")
            raise BlenderProcessError(error_msg) from e

    def _build_blender_command(
        self,
        glb_file_path: str,
        json_file_path: str,
        output_file_path: str,
        blend_file_path: str | None = None,
    ) -> list[str]:
        """
        Build the Blender command arguments.

        Args:
            glb_file_path: Path to the GLB file.
            json_file_path: Path to the JSON configuration file.
            output_file_path: Path for the output file.
            blend_file_path: Optional path to the blend file.

        Returns:
            List of command arguments.
        """

        if not blend_file_path:
            blend_file_path = BLEND_BASE_FILE

        command = [
            BLENDER_APP,
            blend_file_path,
            "--background",
            "--python",
            BLENDER_SCRIPT_FILE,
            "--",
            f"--json_file_path={json_file_path}",
            f"--glb_file_path={glb_file_path}",
            f"--out_file_path={output_file_path}",
            f"--function={BLENDER_FUNCTION_NAME}",
        ]

        return [arg for arg in command if arg is not None]

    def _validate_file_paths(
        self, glb_file_path: str, json_data: dict[str, Any]
    ) -> None:
        """
        Validate input file paths and data.

        Args:
            glb_file_path: Path to the GLB file.
            json_data: JSON configuration data.

        Raises:
            BlenderProcessError: If validation fails.
        """
        if not glb_file_path or not isinstance(glb_file_path, str):
            raise BlenderProcessError("Invalid GLB file path provided")

        if not Path(glb_file_path).exists():
            raise BlenderProcessError(f"GLB file not found: {glb_file_path}")

        if not json_data or not isinstance(json_data, dict):
            raise BlenderProcessError("Invalid JSON data provided")

    def _generate_unique_filename(self) -> str:
        """
        Generate a unique filename.

        Returns:
            A unique filename string.
        """
        return "".join(
            random.choices(
                string.ascii_uppercase + string.digits, k=UNIQUE_FILENAME_LENGTH
            )
        )

    def render_image_process(
        self,
        glb_file_path: str,
        json_file_path: str,
        output_file_path: str,
        blend_file_path: str | None = None,
    ) -> bool:
        """
        Execute the Blender rendering process.

        Args:
            glb_file_path: Path to the GLB file.
            json_file_path: Path to the JSON configuration file.
            output_file_path: Path for the output file.
            blend_file_path: Optional path to the blend file.

        Returns:
            True if rendering was successful, False otherwise.

        Raises:
            BlenderProcessError: If the rendering process fails.
        """
        command = self._build_blender_command(
            glb_file_path, json_file_path, output_file_path, blend_file_path
        )

        logger.info(f"Starting Blender process for output: {output_file_path}")

        try:
            # Execute the command (output is now handled in _execute_command)
            for _ in self._execute_command(command):
                pass  # Output is already displayed in _execute_command

            # Check if output file was created
            if Path(output_file_path).exists():
                logger.info(f"✅ Output file created: {output_file_path}")
                return True
            else:
                logger.warning(f"⚠️ Output file not found: {output_file_path}")
                return False

        except BlenderProcessError:
            logger.error(f"❌ Blender process failed for output: {output_file_path}")
            raise

    def render_video_from_glb(
        self,
        glb_file_path: str,
        json_data: dict[str, Any],
        blend_file_path: str | None = None,
    ) -> str:
        """
        Render a video from GLB file and JSON configuration.

        Args:
            glb_file_path: Path to the GLB file.
            json_data: JSON configuration data.
            blend_file_path: Optional path to the blend file.

        Returns:
            Path to the rendered video file.

        Raises:
            BlenderProcessError: If rendering fails.
        """
        # Validate inputs
        self._validate_file_paths(glb_file_path, json_data)

        # Generate unique filename
        unique_filename = self._generate_unique_filename()

        # Create file paths
        json_file_path = TEMP_DIRECTORY / f"in_{unique_filename}.json"
        video_output_path = TEMP_DIRECTORY / f"out_{unique_filename}.mov"

        try:
            # Write JSON data to temporary file
            FileHandler.write_json_file(file_path=str(json_file_path), data=json_data)
            logger.info(f"JSON configuration written to: {json_file_path}")

            # Use provided blend file or default from environment
            if not blend_file_path:
                blend_file_path = BLEND_BASE_FILE

            # Execute rendering process
            success = self.render_image_process(
                glb_file_path,
                str(json_file_path),
                str(video_output_path),
                blend_file_path,
            )

            if not success:
                raise BlenderProcessError("Rendering process failed")

            return str(video_output_path)

        except Exception as e:
            # Clean up temporary files on error
            for temp_file in [json_file_path, video_output_path]:
                if temp_file.exists():
                    try:
                        temp_file.unlink()
                        logger.info(f"Cleaned up temporary file: {temp_file}")
                    except OSError as cleanup_error:
                        logger.warning(
                            f"Failed to clean up {temp_file}: {cleanup_error}"
                        )

            if isinstance(e, BlenderProcessError):
                raise
            else:
                raise BlenderProcessError(
                    f"Unexpected error during rendering: {e}"
                ) from e
