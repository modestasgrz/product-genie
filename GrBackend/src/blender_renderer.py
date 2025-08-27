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
from typing import Any, Literal

from src.config import (
    BLEND_BASE_FILE,
    BLENDER_APP,
    BLENDER_FUNCTION_NAME,
    BLENDER_SCRIPT_FILE,
)
from src.file_handler import FileHandler
from utils.exceptions import BlenderProcessError
from utils.logger import logger

# Constants
TEMP_DIRECTORY = Path(__file__).parent.parent / "temp_dir"
UNIQUE_FILENAME_LENGTH = 12

RenderEnvironment = Literal["local", "gcp"]
JobStatus = Literal["SUCCESS", "FAILED", "PENDING"]


class BlenderRenderer:
    """
    Handles Blender rendering operations.

    This class encapsulates all Blender-related functionality including
    command execution and file processing.
    """

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
        Execute a command
        """
        command_str = " ".join(command)
        logger.info("🎬 Starting local Blender process...")
        logger.debug(f"Command: {command_str}")

        try:
            with subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            ) as process:
                if process.stdout:
                    for line in iter(process.stdout.readline, ""):
                        line = line.rstrip()
                        if line:
                            logger.info(f"Blender: {line}")
                            yield line
                return_code = process.wait()
                if return_code != 0:
                    raise BlenderProcessError(
                        f"Blender process failed with return code {return_code}",
                        return_code,
                    )
        except FileNotFoundError as e:
            raise BlenderProcessError(
                f"Blender executable not found: {command[0]}"
            ) from e
        except Exception as e:
            raise BlenderProcessError(
                f"Unexpected error executing Blender command: {e}"
            ) from e

    def _build_blender_command(
        self,
        glb_file_path: str,
        json_file_path: str,
        output_file_path: str,
        blend_file_path: str | None = None,
    ) -> list[str]:
        """
        Build the Blender command arguments.
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
        return [str(arg) for arg in command if arg is not None]

    def _validate_file_paths(
        self, glb_file_path: str, json_data: dict[str, Any]
    ) -> None:
        """
        Validate input file paths and data.
        """
        if not glb_file_path or not Path(glb_file_path).exists():
            raise BlenderProcessError(f"GLB file not found: {glb_file_path}")
        if not json_data or not isinstance(json_data, dict):
            raise BlenderProcessError("Invalid JSON data provided")

    def _generate_unique_filename(self, extension: str = "") -> str:
        """
        Generate a unique filename.
        """
        return f"{
            ''.join(
                random.choices(
                    string.ascii_uppercase + string.digits, k=UNIQUE_FILENAME_LENGTH
                )
            )
        }{extension}"

    def render_video_from_glb(
        self,
        glb_file_path: str,
        json_data: dict[str, Any],
        blend_file_path: str | None = None,
    ) -> str | dict[str, Any]:
        """
        Render a video from a GLB file and JSON configuration.
        """
        self._validate_file_paths(glb_file_path, json_data)

        unique_filename = self._generate_unique_filename()
        json_file_path = TEMP_DIRECTORY / f"in_{unique_filename}.json"
        video_output_path = TEMP_DIRECTORY / f"out_{unique_filename}.mov"

        try:
            FileHandler.write_json_file(str(json_file_path), json_data)
            command = self._build_blender_command(
                glb_file_path,
                str(json_file_path),
                str(video_output_path),
                blend_file_path,
            )

            for _ in self._execute_command(command):
                pass

            if not video_output_path.exists():
                raise BlenderProcessError("Rendered video file not found.")

            return str(video_output_path)

        finally:
            # Clean up temporary JSON file
            if json_file_path.exists():
                json_file_path.unlink()
