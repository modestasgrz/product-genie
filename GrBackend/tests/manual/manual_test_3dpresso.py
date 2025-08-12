import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from d_presso_domain.d_presso import DPressoService
from d_presso_domain.d_presso_schemas import VideoTo3DParams, VideoTo3DRequest
from src.config import D_PRESSO_API_KEY, D_PRESSO_BASE_URL
from utils.logger import logger


def test_video_to_3d_workflow(
    input_file_path: str | Path, output_glb_path: str | Path, polling_interval: int = 10
):
    service = DPressoService(api_key=D_PRESSO_API_KEY, base_url=D_PRESSO_BASE_URL)

    input_file_path = Path(input_file_path)
    output_glb_path = Path(output_glb_path)

    # 1. Initiate the Video to 3D task
    file_name = input_file_path.name
    file_size = input_file_path.stat().st_size

    request_data = VideoTo3DRequest(
        engineName="video_to_3d",
        fileName=file_name,
        fileSize=file_size,
        params=VideoTo3DParams(remove_floor=True),
        uploadContext={},
        metadata={},
        destinationContext={
            "type": "s3",
            "bucketName": "your-s3-bucket-name",
            "accessKeyId": "your-access-key-id",
            "secretAccessKey": "your-secret-access-key",
            "folder": "3d_presso_results/",
        },
        callbackUrl="https://example.com/callback",
    )

    logger.info(f"Initiating Video to 3D task for {file_name}...")
    try:
        response = service.video_to_3d(request_data)
        task_id = response.id
        upload_url = response.uploadUrl

        logger.info(f"Task initiated. Task ID: {task_id}")
        if upload_url:
            logger.info(f"Upload URL received: {upload_url}")
            # 2. Upload the video file
            logger.info(f"Uploading video file from {input_file_path}...")
            service.upload_video_file(upload_url, input_file_path)
            logger.info("Video file uploaded successfully.")
        else:
            logger.warning(
                "No upload URL received. Check API response or configuration."
            )
            return

        # 3. Poll for task status and retrieve result
        status = ""
        while status not in ["SUCCEEDED", "FAILED", "CANCELLED"]:
            logger.info(f"Polling for task status (current status: {status})...")
            time.sleep(polling_interval)  # Wait for 10 seconds before polling again
            task_status_response = service.get_video_to_3d_result(task_id)
            status = task_status_response.status
            logger.info(f"Task status: {status}")

            if status == "SUCCEEDED":
                glb_url = task_status_response.output.get(
                    "modelUrl"
                )  # Assuming 'modelUrl' is the key for GLB
                if glb_url:
                    logger.info(f"Task succeeded. GLB model URL: {glb_url}")
                    # 4. Download the GLB model
                    logger.info(f"Downloading GLB model to {output_glb_path}...")
                    service.download_glb_model(glb_url, output_glb_path)
                    logger.info(f"GLB model downloaded to {output_glb_path}")
                else:
                    logger.warning(
                        "GLB model URL not found in successful task response."
                    )
            elif status in ["FAILED", "CANCELLED"]:
                logger.error(f"Task {status}. Error: {task_status_response.task_error}")
                break

    except Exception as e:
        logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    test_video_to_3d_workflow(
        input_file_path=Path(__file__).parent.parent.parent
        / "Data"
        / "3d_presso_test_data"
        / "IMG_2332.MOV",
        output_glb_path=Path(__file__).parent.parent.parent
        / "Data"
        / "3d_presso_results"
        / "output.glb",
    )
