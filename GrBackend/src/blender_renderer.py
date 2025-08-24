"""
API Process Module

This module handles video rendering processes using Blender.
It provides functionality to execute Blender commands and render images/videos
from GLB files and JSON configurations.
"""

import os
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
    RENDER_ENVIRONMENT,
)
from src.file_handler import FileHandler
from src.gce import GCEManager
from src.gcs import GCSManager
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

    def __init__(self) -> None:
        """Initialize the BlenderRenderer with environment validation."""
        self._ensure_temp_directory()
        self.render_environment = self._get_render_environment()
        self.gce_manager: GCEManager | None = None
        self.gcs_manager: GCSManager | None = None
        if self.render_environment == "gcp":
            self.gce_manager = GCEManager()
            self.gcs_manager = GCSManager()

    def _get_render_environment(self) -> RenderEnvironment:
        """Determine the rendering environment."""
        if RENDER_ENVIRONMENT == "gcp":
            logger.info("GCP render environment configured.")
            return "gcp"
        try:
            if "metadata.google.internal" in os.environ.get(
                "GCE_METADATA_HOST", ""
            ) or os.environ.get("K_SERVICE"):
                logger.info("Running on GCP, setting render environment to 'gcp'.")
                return "gcp"
        except Exception:
            pass
        logger.info("Defaulting to 'local' render environment.")
        return "local"

    def _ensure_temp_directory(self) -> None:
        """Ensure the temporary directory exists."""
        try:
            TEMP_DIRECTORY.mkdir(parents=True, exist_ok=True)
            logger.info(f"Temporary directory ensured: {TEMP_DIRECTORY}")
        except OSError as e:
            logger.error(f"Failed to create temporary directory: {e}")
            raise BlenderProcessError(f"Cannot create temporary directory: {e}") from e

    def _execute_local_command(self, command: list[str]) -> Generator[str, None, None]:
        """
        Execute a command locally and yield stdout lines.
        """
        command_str = " ".join(command)
        logger.info("🎬 Starting local Blender process...")
        logger.debug(f"Command: {command_str}")

        try:
            with subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
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

    def get_gcp_job_status(self, job_id: str) -> JobStatus:
        """
        Checks the status of a GCP render job by looking for marker files.
        """
        if not self.gcs_manager:
            raise BlenderProcessError("GCS Manager not initialized.")

        success_marker = f"renders/{job_id}/_SUCCESS"
        failure_marker = f"renders/{job_id}/_FAILED"

        if self.gcs_manager.file_exists(success_marker):
            return "SUCCESS"
        if self.gcs_manager.file_exists(failure_marker):
            return "FAILED"
        return "PENDING"

    def render_video_from_glb(
        self,
        glb_file_path: str,
        json_data: dict[str, Any],
        blend_file_path: str | None = None,
    ) -> str | dict[str, Any]:
        """
        Render a video from a GLB file and JSON configuration.
        This method orchestrates the rendering process, either locally or on GCP.

        For local renders, it returns the path to the output file.
        For GCP renders, it returns a dictionary with job tracking information.
        """
        self._validate_file_paths(glb_file_path, json_data)

        if self.render_environment == "gcp":
            if not self.gce_manager or not self.gcs_manager:
                raise BlenderProcessError("GCP Managers not initialized.")

            job_id = self._generate_unique_filename()
            base_path = f"renders/{job_id}"
            gcs_input_glb_path = f"{base_path}/input.glb"
            gcs_input_json_path = f"{base_path}/input.json"
            gcs_output_video_path = f"{base_path}/output.mov"
            gcs_success_marker = f"{base_path}/_SUCCESS"
            gcs_failure_marker = f"{base_path}/_FAILED"

            # Upload assets to GCS
            self.gcs_manager.upload_file(glb_file_path, gcs_input_glb_path)
            self.gcs_manager.upload_json_data(json_data, gcs_input_json_path)

            # Launch the VM
            for log in self.gce_manager.launch_render_vm(
                f"gs://{self.gcs_manager.bucket_name}/{gcs_input_glb_path}",
                f"gs://{self.gcs_manager.bucket_name}/{gcs_input_json_path}",
                f"gs://{self.gcs_manager.bucket_name}/{gcs_output_video_path}",
                f"gs://{self.gcs_manager.bucket_name}/{gcs_success_marker}",
                f"gs://{self.gcs_manager.bucket_name}/{gcs_failure_marker}",
            ):
                logger.info(log)

            return {
                {
                    "job_id": job_id,
                    "gcs_output_video_path": gcs_output_video_path,
                    "gcs_success_marker_path": gcs_success_marker,
                    "gcs_failure_marker_path": gcs_failure_marker,
                }
            }

        else:  # Local rendering
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

                for log in self._execute_local_command(command):
                    logger.info(log)

                if not video_output_path.exists():
                    raise BlenderProcessError("Rendered video file not found.")

                return str(video_output_path)

            finally:
                # Clean up temporary JSON file
                if json_file_path.exists():
                    json_file_path.unlink()
