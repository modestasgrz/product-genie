"""
GCE Management Module

This module provides a class to manage Google Compute Engine (GCE) instances
for running Blender rendering jobs.
"""

import random
import string
from collections.abc import Generator

import google.cloud.compute_v1

from src.config import (
    BLEND_BASE_FILE,
    BLENDER_APP,
    BLENDER_FUNCTION_NAME,
    BLENDER_SCRIPT_FILE,
    GCP_CONTAINER_IMAGE,
    GCP_MACHINE_TYPE,
    GCP_PROJECT_ID,
    GCP_SERVICE_ACCOUNT_EMAIL,
    GCP_VM_MAX_RUN_DURATION_SECONDS,
    GCP_ZONE,
    GCS_BUCKET_NAME,
)
from utils.exceptions import BlenderProcessError
from utils.logger import logger


class GCEManager:
    """
    Manages the lifecycle of GCE VMs for rendering tasks.
    """

    def __init__(self) -> None:
        """
        Initializes the GCEManager, checking for required GCP configuration.
        """
        if not all([GCP_PROJECT_ID, GCP_ZONE, GCP_CONTAINER_IMAGE, GCS_BUCKET_NAME]):
            msg = (
                "GCP configuration (PROJECT_ID, ZONE, CONTAINER_IMAGE, GCS_BUCKET_NAME)"
                "is missing."
            )
            logger.error(msg)
            raise BlenderProcessError(msg)
        self.instances_client = google.cloud.compute_v1.InstancesClient()

    def _build_instance_config(
        self,
        instance_name: str,
        gcs_input_glb: str,
        gcs_input_json: str,
        gcs_output_video: str,
        gcs_success_marker: str,
        gcs_failure_marker: str,
    ) -> dict:
        """
        Builds the configuration dictionary for a new GCE instance.
        """
        machine_type = f"zones/{GCP_ZONE}/machineTypes/{GCP_MACHINE_TYPE}"

        startup_script = f"""#!/bin/bash
# Fail fast on any error
set -e
set -o pipefail

# --- Configuration ---
VM_DATA_DIR="/data"
VM_LOG_FILE="${{VM_DATA_DIR}}/render_log.txt"
VM_INPUT_GLB="${{VM_DATA_DIR}}/scene.glb"
VM_INPUT_JSON="${{VM_DATA_DIR}}/config.json"
VM_OUTPUT_VIDEO="${{VM_DATA_DIR}}/render_output.mov"
INSTANCE_NAME="{instance_name}"
ZONE="{GCP_ZONE}"

# --- Cleanup Function ---
# This function will be called on script exit or error to ensure cleanup.
cleanup() {{
    EXIT_CODE=$?
    if [ $EXIT_CODE -ne 0 ]; then
        echo "Render script failed with exit code $EXIT_CODE." | tee -a ${{VM_LOG_FILE}}
        echo "Uploading failure marker and logs..." | tee -a ${{VM_LOG_FILE}}
        # Upload the log file to GCS for debugging
        gcloud storage cp ${{VM_LOG_FILE}} {gcs_failure_marker} || echo "Failed to upload log file."
    fi
    # Self-delete the VM
    echo "VM self-destructing..." | tee -a ${{VM_LOG_FILE}}
    gcloud compute instances delete ${{INSTANCE_NAME}} --zone=${{ZONE}} --quiet
}}
trap cleanup EXIT

# --- Execution ---
# 1. Create a local directory on the VM to store data and redirect all output to log
mkdir -p ${{VM_DATA_DIR}}
exec > >(tee -a ${{VM_LOG_FILE}}) 2>&1

echo "Starting render process..."
echo "Downloading input files from GCS..."
# 2. Download the input files from GCS to the VM's local disk
gcloud storage cp {gcs_input_glb} ${{VM_INPUT_GLB}}
gcloud storage cp {gcs_input_json} ${{VM_INPUT_JSON}}

echo "Running Blender container..."
# 3. Run the Blender container with a timeout
timeout {GCP_VM_MAX_RUN_DURATION_SECONDS}s docker run \
    -v ${{VM_DATA_DIR}}:${{VM_DATA_DIR}} \
    {GCP_CONTAINER_IMAGE} \
    {BLENDER_APP} -b {BLEND_BASE_FILE} --python {BLENDER_SCRIPT_FILE} -- \
    --glb_file_path=${{VM_INPUT_GLB}} \
    --json_file_path=${{VM_INPUT_JSON}} \
    --out_file_path=${{VM_OUTPUT_VIDEO}} \
    --function={BLENDER_FUNCTION_NAME}

echo "Blender process finished. Uploading results..."
# 4. Upload the rendered video back to GCS
gcloud storage cp ${{VM_OUTPUT_VIDEO}} {gcs_output_video}

# 5. Upload a success marker to GCS
gcloud storage cp /dev/null {gcs_success_marker}

echo "Render successful. VM will now self-destruct."
# The cleanup trap will handle the deletion.
"""  # noqa: E501

        return {
            {
                "name": instance_name,
                "machine_type": machine_type,
                "disks": [
                    {
                        {
                            "boot": True,
                            "auto_delete": True,
                            "initialize_params": {
                                {
                                    "source_image": "projects/cos-cloud/global/images/family/cos-stable",  # noqa: E501
                                }
                            },
                        }
                    }
                ],
                "network_interfaces": [{{"network": "global/networks/default"}}],
                "service_accounts": [
                    {
                        {
                            "email": GCP_SERVICE_ACCOUNT_EMAIL,
                            "scopes": [
                                "https://www.googleapis.com/auth/cloud-platform"
                            ],
                        }
                    }
                ],
                "metadata": {
                    {
                        "items": [
                            {
                                {
                                    "key": "startup-script",
                                    "value": startup_script,
                                }
                            }
                        ]
                    }
                },
            }
        }

    def launch_render_vm(
        self,
        gcs_input_glb: str,
        gcs_input_json: str,
        gcs_output_video: str,
        gcs_success_marker: str,
        gcs_failure_marker: str,
    ) -> Generator[str, None, None]:
        """
        Creates a GCE VM that runs a Blender command in a container and then
        self-destructs.
        """
        instance_name = f"render-job-{
            ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        }"

        logger.info(f"🚀 Launching GCE VM '{instance_name}' for rendering...")

        config = self._build_instance_config(
            instance_name,
            gcs_input_glb,
            gcs_input_json,
            gcs_output_video,
            gcs_success_marker,
            gcs_failure_marker,
        )

        try:
            self.instances_client.insert(
                project=GCP_PROJECT_ID,
                zone=GCP_ZONE,
                instance_resource=config,  # type: ignore[arg-type]
            )
            logger.info(
                f"Instance {instance_name} creation initiated in project "
                f"{GCP_PROJECT_ID}, zone {GCP_ZONE}."
            )
            yield f"VM creation for {instance_name} initiated."
            yield (
                f"VM {instance_name} is running the render job. "
                f"It will self-destruct upon completion."
            )
            logger.info(
                "VM creation initiated. It will run the render and self-destruct."
            )

        except Exception as e:
            error_msg = f"Failed to create GCE VM: {e}"
            logger.error(f"❌ {error_msg}")
            raise BlenderProcessError(error_msg) from e
