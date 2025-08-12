import sys
import time
from pathlib import Path

from PIL import Image

# Add the parent directory of GrBackend to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from meshy_ai_domain.meshy_ai import MeshyAIService
from meshy_ai_domain.meshy_schemas import MultiImageTo3DRequest
from src.config import MESHY_API_KEY, MESHY_BASE_URL
from utils.logger import logger


def run_meshy_ai_test(
    meshy_service: MeshyAIService,
    images: list[Image.Image],
    output_dir: Path,
    polling_interval: int = 10,
) -> None:
    """
    Tests the MeshyAIService by attempting to call the multi-image-to-3d API
    and then retrieve its status.
    """
    if not MESHY_API_KEY:
        logger.error("Error: MESHY_API_KEY is not set in GrBackend/.env")
        logger.error("Please set the MESHY_API_KEY before running this test.")
        return

    if not MESHY_BASE_URL:
        logger.error("Error: MESHY_BASE_URL is not set in GrBackend/.env")
        logger.error("Please set the MESHY_BASE_URL before running this test.")
        return

    logger.info(f"Attempting to call Meshy AI with base URL: {MESHY_BASE_URL}")
    try:
        # --- Test Multi-Image-to-3D Render ---
        logger.info("\n--- Testing Multi-Image-to-3D Render ---")
        multi_image_request_data = {
            "images": images,
            "target_polycount": 300000,
            "should_texture": False,
        }
        render_request = MultiImageTo3DRequest(**multi_image_request_data)  # type: ignore[arg-type]
        try:
            render_response = meshy_service.multi_image_to_3d(render_request)
            task_id = render_response.result
            logger.info(f"Render Request Sent. Task ID: {task_id}")

            # --- Test 3D Object Render Retrieval ---
            logger.info("\n--- Testing 3D Object Render Retrieval ---")
            logger.info(
                f"Waiting for task {task_id} to complete "
                f"(polling every {polling_interval} seconds)..."
            )
            status = "PENDING"
            while status in ["PENDING", "IN_PROGRESS"]:
                time.sleep(
                    polling_interval
                )  # Wait for polling_interval seconds before polling again
                retrieve_response = meshy_service.get_multi_image_to_3d_result(task_id)
                status = retrieve_response.status
                logger.info(f"Task {task_id} current status: {status}")

                if status == "SUCCEEDED":
                    logger.info(f"Task {task_id} succeeded!")
                    if (
                        retrieve_response.model_urls
                        and retrieve_response.model_urls.glb
                    ):
                        glb_url = retrieve_response.model_urls.glb
                        logger.info(f"GLB Model URL: {glb_url}")
                        output_file_path = output_dir / f"{task_id}.glb"

                        try:
                            downloaded_path = meshy_service.download_glb_model(
                                glb_url, output_file_path
                            )
                            logger.info(f"Downloaded GLB model to: {downloaded_path}")
                        except Exception as download_e:
                            logger.error(f"Failed to download GLB model: {download_e}")

                    if retrieve_response.texture_urls:
                        for i, texture in enumerate(retrieve_response.texture_urls):
                            logger.info(
                                f"Texture {i + 1} Base Color URL: {texture.base_color}"
                            )
                    break
                elif status == "FAILED":
                    logger.error(f"Task {task_id} failed.")
                    break
            logger.info(
                "\nMeshy AI test completed successfully (or task finished/failed)!"
            )

        except Exception as e:
            logger.error(f"\nMeshy AI test failed during render or retrieval: {e}")

    except ValueError as e:
        logger.error(f"\nMeshy AI service initialization failed: {e}")
    except Exception as e:
        logger.error(f"\nAn unexpected error occurred during Meshy AI test: {e}")


if __name__ == "__main__":
    meshy_service = MeshyAIService()
    data_dir_path = Path(__file__).parent.parent.parent / "Data" / "meshy_ai_test_data"
    output_dir = Path(__file__).parent.parent.parent / "Data" / "meshy_ai_results"
    images = [
        Image.open(img_path)
        for img_path in data_dir_path.iterdir()
        if ".png" in str(img_path)
    ]
    run_meshy_ai_test(meshy_service, images, output_dir, polling_interval=5)  # type: ignore[arg-type]
