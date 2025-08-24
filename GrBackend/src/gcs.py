"""
GCS Management Module

This module provides a class to manage Google Cloud Storage (GCS) operations.
"""

import json

from google.cloud import storage

from src.config import GCS_BUCKET_NAME
from utils.exceptions import GCSExchangeError
from utils.logger import logger


class GCSManager:
    """
    Manages file operations with Google Cloud Storage.
    """

    def __init__(self) -> None:
        """
        Initializes the GCSManager and the storage client.
        """
        if not GCS_BUCKET_NAME:
            raise ValueError("GCS_BUCKET_NAME is not set in the configuration.")
        self.storage_client = storage.Client()
        self.bucket_name = GCS_BUCKET_NAME
        self.bucket = self.storage_client.bucket(self.bucket_name)

    def upload_file(self, local_path: str, gcs_path: str) -> str:
        """
        Uploads a local file to a GCS bucket.

        Args:
            local_path: The path to the local file.
            gcs_path: The destination path in the GCS bucket.

        Returns:
            The GCS URI of the uploaded file.
        """
        try:
            logger.info(f"Uploading {local_path} to gs://{self.bucket_name}/{gcs_path}")
            blob = self.bucket.blob(gcs_path)
            blob.upload_from_filename(local_path)
            logger.info("File uploaded successfully.")
            return f"gs://{self.bucket_name}/{gcs_path}"
        except Exception as e:
            logger.error(f"Failed to upload file to GCS: {e}")
            raise GCSExchangeError(f"Failed to upload {local_path} to GCS.") from e

    def upload_json_data(self, data: dict, gcs_path: str) -> str:
        """
        Uploads a dictionary as a JSON file to a GCS bucket.

        Args:
            data: The dictionary data to upload.
            gcs_path: The destination path in the GCS bucket for the JSON file.

        Returns:
            The GCS URI of the uploaded file.
        """
        try:
            logger.info(f"Uploading JSON data to gs://{self.bucket_name}/{gcs_path}")
            blob = self.bucket.blob(gcs_path)
            blob.upload_from_string(
                json.dumps(data, indent=4),
                content_type="application/json",
            )
            logger.info("JSON data uploaded successfully.")
            return f"gs://{self.bucket_name}/{gcs_path}"
        except Exception as e:
            logger.error(f"Failed to upload JSON data to GCS: {e}")
            raise GCSExchangeError("Failed to upload JSON data to GCS.") from e

    def file_exists(self, gcs_path: str) -> bool:
        """
        Checks if a file exists in the GCS bucket.

        Args:
            gcs_path: The path of the file in the GCS bucket.

        Returns:
            True if the file exists, False otherwise.
        """
        try:
            blob = self.bucket.blob(gcs_path)
            return blob.exists()
        except Exception as e:
            logger.error(f"Error checking for file {gcs_path} in GCS: {e}")
            # In case of an error, assume the file doesn't exist to be safe.
            return False

    def upload_empty_file(self, gcs_path: str) -> str:
        """
        Uploads an empty file to a GCS bucket, often used as a marker.

        Args:
            gcs_path: The destination path in the GCS bucket.

        Returns:
            The GCS URI of the uploaded file.
        """
        try:
            logger.info(f"Uploading empty marker file to gs://{self.bucket_name}/{gcs_path}")
            blob = self.bucket.blob(gcs_path)
            blob.upload_from_string("", content_type="text/plain")
            logger.info("Empty file uploaded successfully.")
            return f"gs://{self.bucket_name}/{gcs_path}"
        except Exception as e:
            logger.error(f"Failed to upload empty file to GCS: {e}")
            raise GCSExchangeError("Failed to upload empty file to GCS.") from e
