"""
File Handler Module

This module provides comprehensive file handling utilities including:
- ZIP file operations (compression, extraction, creation)
- Binary file operations (read/write)
- CSV file operations (read/write)
- JSON file operations (read/write)
- Directory traversal and file discovery
- Base64 encoding/decoding for file data

The module is designed to handle various file formats and provides
robust error handling and validation for file operations.
"""

import base64
import binascii  # Import binascii directly
import json
import os
from pathlib import Path
from typing import Any
from zipfile import BadZipFile, ZipFile

import numpy as np
import numpy.typing as npt

from utils.exceptions import FileHandlerError
from utils.logger import logger

# Type aliases for better readability
JsonData = dict[str, Any] | list[Any] | str | int | float | bool | None


class FileHandler:
    """
    Comprehensive file handling utility class.

    This class provides static methods for various file operations
    including ZIP handling, binary operations, CSV operations,
    and JSON operations with proper error handling and validation.
    """

    @staticmethod
    def _ensure_directory_exists(file_path: str | Path) -> None:
        """
        Ensure the directory for a file path exists.

        Args:
            file_path: Path to the file whose directory should be created.

        Raises:
            FileHandlerError: If directory creation fails.
        """
        try:
            directory = Path(file_path).parent
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directory ensured: {directory}")
        except OSError as e:
            error_msg = f"Failed to create directory for {file_path}: {e}"
            logger.error(error_msg)
            raise FileHandlerError(error_msg, str(file_path)) from e

    # Dictionary Operations
    @staticmethod
    def update_nested_dict(
        target_dict: dict[str, Any], update_dict: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Recursively update a nested dictionary.

        Args:
            target_dict: Dictionary to be updated.
            update_dict: Dictionary containing updates.

        Returns:
            Updated dictionary.

        Raises:
            FileHandlerError: If inputs are not dictionaries.
        """
        if not isinstance(target_dict, dict) or not isinstance(update_dict, dict):
            raise FileHandlerError("Both arguments must be dictionaries")

        try:
            for key, value in update_dict.items():
                if (
                    isinstance(value, dict)
                    and key in target_dict
                    and isinstance(target_dict[key], dict)
                ):
                    target_dict[key] = FileHandler.update_nested_dict(
                        target_dict[key], value
                    )
                else:
                    target_dict[key] = value
            return target_dict
        except Exception as e:
            raise FileHandlerError(f"Failed to update nested dictionary: {e}") from e

    # ZIP File Operations
    @staticmethod
    def extract_zip_file(
        zip_file_path: str | Path, extract_directory: str | Path
    ) -> None:
        """
        Extract a ZIP file to a specified directory.

        Args:
            zip_file_path: Path to the ZIP file.
            extract_directory: Directory to extract files to.

        Raises:
            FileHandlerError: If extraction fails.
        """
        extract_path = Path(extract_directory)

        try:
            # Ensure extraction directory exists
            extract_path.mkdir(parents=True, exist_ok=True)

            with ZipFile(zip_file_path, "r") as zip_file:
                zip_file.extractall(extract_path)
                logger.info(f"Successfully extracted {zip_file_path} to {extract_path}")

        except BadZipFile as e:
            error_msg = f"Invalid ZIP file: {zip_file_path}"
            logger.error(error_msg)
            raise FileHandlerError(error_msg, str(zip_file_path)) from e
        except Exception as e:
            error_msg = f"Failed to extract ZIP file {zip_file_path}: {e}"
            logger.error(error_msg)
            raise FileHandlerError(error_msg, str(zip_file_path)) from e

    @staticmethod
    def compress_directory_to_zip(
        zip_file_path: str | Path, source_directory: str | Path
    ) -> None:
        """
        Compress a directory into a ZIP file.

        Args:
            zip_file_path: Path for the output ZIP file.
            source_directory: Directory to compress.

        Raises:
            FileHandlerError: If compression fails.
        """
        zip_path = Path(zip_file_path)

        try:
            # Ensure output directory exists
            FileHandler._ensure_directory_exists(zip_path)

            # Get all file paths in the directory
            file_paths = FileHandler.get_all_file_paths(source_directory)

            with ZipFile(zip_path, "w") as zip_file:
                for file_path in file_paths:
                    # Use relative path within the ZIP
                    arcname = Path(file_path).relative_to(source_directory)
                    zip_file.write(file_path, arcname)

            logger.info(f"Successfully compressed {source_directory} to {zip_path}")

        except Exception as e:
            error_msg = f"Failed to compress directory {source_directory} to ZIP: {e}"
            logger.error(error_msg)
            raise FileHandlerError(error_msg, str(source_directory)) from e

    @staticmethod
    def create_zip_from_files(
        zip_file_path: str | Path, file_paths: list[str | Path]
    ) -> None:
        """
        Create a ZIP file from a list of file paths.

        Args:
            zip_file_path: Path for the output ZIP file.
            file_paths: List of file paths to include in the ZIP.

        Raises:
            FileHandlerError: If ZIP creation fails.
        """
        if not file_paths:
            raise FileHandlerError("No file paths provided for ZIP creation")

        zip_path = Path(zip_file_path)

        try:
            # Ensure output directory exists
            FileHandler._ensure_directory_exists(zip_path)

            with ZipFile(zip_path, "w") as zip_file:
                for file_path in file_paths:
                    file_path = Path(file_path)
                    # Use just the filename as the archive name
                    zip_file.write(file_path, file_path.name)

            logger.info(
                f"Successfully created ZIP file {zip_path} with {len(file_paths)} files"
            )

        except Exception as e:
            error_msg = f"Failed to create ZIP file {zip_file_path}: {e}"
            logger.error(error_msg)
            raise FileHandlerError(error_msg, str(zip_file_path)) from e

    @staticmethod
    def save_base64_as_zip(file_path: str | Path, base64_data: str) -> None:
        """
        Save base64-encoded data as a ZIP file.

        Args:
            file_path: Path where the ZIP file should be saved.
            base64_data: Base64-encoded ZIP data.

        Raises:
            FileHandlerError: If saving fails.
        """
        if not base64_data or not isinstance(base64_data, str):
            raise FileHandlerError("Invalid base64 data provided")

        file_path_obj = Path(file_path)

        try:
            # Ensure output directory exists
            FileHandler._ensure_directory_exists(file_path_obj)

            # Decode base64 data
            zip_data = base64.b64decode(base64_data)

            with open(file_path_obj, "wb") as file_handle:
                file_handle.write(zip_data)

            logger.info(f"Successfully saved base64 data as ZIP file: {file_path_obj}")

        except (binascii.Error, ValueError) as e:  # Use binascii.Error directly
            error_msg = f"Invalid base64 data: {e}"
            logger.error(error_msg)
            raise FileHandlerError(error_msg, str(file_path)) from e
        except Exception as e:
            error_msg = f"Failed to save base64 data as ZIP file {file_path}: {e}"
            logger.error(error_msg)
            raise FileHandlerError(error_msg, str(file_path)) from e

    @staticmethod
    def load_zip_as_base64(file_path: str | Path) -> str:
        """
        Load a ZIP file and return as base64-encoded string.

        Args:
            file_path: Path to the ZIP file.

        Returns:
            Base64-encoded string of the ZIP file.

        Raises:
            FileHandlerError: If loading fails.
        """

        try:
            with open(file_path, "rb") as file_handle:
                zip_data = file_handle.read()

            base64_data = base64.b64encode(zip_data).decode("utf-8")
            logger.info(f"Successfully loaded ZIP file as base64: {file_path}")
            return base64_data

        except Exception as e:
            error_msg = f"Failed to load ZIP file {file_path} as base64: {e}"
            logger.error(error_msg)
            raise FileHandlerError(error_msg, str(file_path)) from e

    # Directory Operations
    @staticmethod
    def get_all_file_paths(directory_path: str | Path) -> list[str]:
        """
        Get all file paths in a directory recursively.

        Args:
            directory: Directory to search.

        Returns:
            List of file paths.

        Raises:
            FileHandlerError: If directory traversal fails.
        """

        try:
            file_paths = []
            for root, _, files in os.walk(directory_path):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    file_paths.append(file_path)

            logger.debug(f"Found {len(file_paths)} files in {directory_path}")
            return file_paths

        except Exception as e:
            error_msg = f"Failed to get file paths from directory {directory_path}: {e}"
            logger.error(error_msg)
            raise FileHandlerError(error_msg, str(directory_path)) from e

    @staticmethod
    def get_files_with_extensions(
        directory_path: str | Path, extensions: list[str]
    ) -> list[str]:
        """
        Get files with specific extensions from a directory.

        Args:
            directory_path: Directory to search.
            extensions: List of file extensions (e.g., ['.txt', '.json']).

        Returns:
            List of file paths with matching extensions.

        Raises:
            FileHandlerError: If search fails.
        """

        if not extensions:
            raise FileHandlerError("No extensions provided")

        # Ensure extensions start with a dot
        normalized_extensions = [
            ext if ext.startswith(".") else f".{ext}" for ext in extensions
        ]

        directory_path = Path(directory_path)
        try:
            files = [
                str(path)
                for path in directory_path.rglob("*")
                if path.is_file() and path.suffix.lower() in normalized_extensions
            ]

            logger.debug(
                f"Found {len(files)} files with extensions {normalized_extensions} ",
                f"in {directory_path}",
            )
            return files

        except Exception as e:
            error_msg = (
                f"Failed to get files with extensions {extensions} from "
                f"{directory_path}: {e}"
            )
            logger.error(error_msg)
            raise FileHandlerError(error_msg, str(directory_path)) from e

    # Binary File Operations
    @staticmethod
    def read_binary_file(file_path: str | Path) -> npt.NDArray[np.uint8]:
        """
        Read a binary file as numpy array.

        Args:
            file_path: Path to the binary file.

        Returns:
            Numpy array containing file data.

        Raises:
            FileHandlerError: If reading fails.
        """

        try:
            data = np.fromfile(file_path, dtype="uint8")
            logger.debug(
                f"Successfully read binary file: {file_path} ({len(data)} bytes)"
            )
            return data

        except Exception as e:
            error_msg = f"Failed to read binary file {file_path}: {e}"
            logger.error(error_msg)
            raise FileHandlerError(error_msg, str(file_path)) from e

    @staticmethod
    def write_binary_file(file_path: str | Path, data: npt.NDArray[np.uint8]) -> None:
        """
        Write numpy array data to a binary file.

        Args:
            file_path: Path where the binary file should be written.
            data: Numpy array data to write.

        Raises:
            FileHandlerError: If writing fails.
        """
        if not isinstance(data, np.ndarray):
            raise FileHandlerError("Data must be a numpy array")

        file_path_obj = Path(file_path)

        try:
            # Ensure output directory exists
            FileHandler._ensure_directory_exists(file_path_obj)

            # Convert to uint8 and write to file
            data.astype("uint8").tofile(file_path_obj)
            logger.info(
                f"Successfully wrote binary file: {file_path_obj} ({len(data)} bytes)"
            )

        except Exception as e:
            error_msg = f"Failed to write binary file {file_path}: {e}"
            logger.error(error_msg)
            raise FileHandlerError(error_msg, str(file_path)) from e

    # CSV File Operations
    @staticmethod
    def read_csv_file(file_path: str | Path) -> np.ndarray:
        """
        Read a CSV file as numpy array.

        Args:
            file_path: Path to the CSV file.

        Returns:
            Numpy array containing CSV data.

        Raises:
            FileHandlerError: If reading fails.
        """

        try:
            data = np.genfromtxt(file_path, delimiter=",", dtype=int)
            logger.info(f"Successfully read CSV file: {file_path}")
            return data

        except Exception as e:
            error_msg = f"Failed to read CSV file {file_path}: {e}"
            logger.error(error_msg)
            raise FileHandlerError(error_msg, str(file_path)) from e

    @staticmethod
    def write_csv_file(
        file_path: str | Path, data: np.ndarray, reshape_size: tuple | None = None
    ) -> None:
        """
        Write numpy array data to a CSV file.

        Args:
            file_path: Path where the CSV file should be written.
            data: Numpy array data to write.
            reshape_size: Optional tuple to reshape data before writing.

        Raises:
            FileHandlerError: If writing fails.
        """
        if not isinstance(data, np.ndarray):
            raise FileHandlerError("Data must be a numpy array")

        file_path_obj = Path(file_path)

        try:
            # Ensure output directory exists
            FileHandler._ensure_directory_exists(file_path_obj)

            # Reshape data if size is provided
            if reshape_size is not None:
                data = data.reshape(reshape_size)

            # Write CSV file
            np.savetxt(file_path_obj, data.astype(int), fmt="%i", delimiter=",")
            logger.info(f"Successfully wrote CSV file: {file_path_obj}")

        except Exception as e:
            error_msg = f"Failed to write CSV file {file_path}: {e}"
            logger.error(error_msg)
            raise FileHandlerError(error_msg, str(file_path)) from e

    # JSON File Operations
    @staticmethod
    def read_json_file(file_path: str | Path) -> JsonData:
        """
        Read a JSON file and return parsed data.

        Args:
            file_path: Path to the JSON file.

        Returns:
            Parsed JSON data.

        Raises:
            FileHandlerError: If reading or parsing fails.
        """

        try:
            with open(file_path, encoding="utf-8") as file_handle:
                data = json.load(file_handle)

            logger.info(f"Successfully read JSON file: {file_path}")
            return data  # type: ignore[no-any-return]

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in file {file_path}: {e}"
            logger.error(error_msg)
            raise FileHandlerError(error_msg, str(file_path)) from e
        except Exception as e:
            error_msg = f"Failed to read JSON file {file_path}: {e}"
            logger.error(error_msg)
            raise FileHandlerError(error_msg, str(file_path)) from e

    @staticmethod
    def write_json_file(file_path: str | Path, data: JsonData, indent: int = 4) -> None:
        """
        Write data to a JSON file with proper formatting.

        Args:
            file_path: Path where the JSON file should be written.
            data: Data to write as JSON.
            indent: Number of spaces for indentation (default: 4).

        Raises:
            FileHandlerError: If writing fails.
        """
        file_path_obj = Path(file_path)

        try:
            # Ensure output directory exists
            FileHandler._ensure_directory_exists(file_path_obj)

            with open(file_path_obj, "w", encoding="utf-8") as file_handle:
                json_string = json.dumps(
                    data,
                    indent=indent,
                    sort_keys=True,
                    separators=(",", ": "),
                    ensure_ascii=False,
                )
                file_handle.write(json_string)

            logger.info(f"Successfully wrote JSON file: {file_path_obj}")

        except (TypeError, ValueError) as e:
            error_msg = f"Data is not JSON serializable: {e}"
            logger.error(error_msg)
            raise FileHandlerError(error_msg, str(file_path)) from e
        except Exception as e:
            error_msg = f"Failed to write JSON file {file_path}: {e}"
            logger.error(error_msg)
            raise FileHandlerError(error_msg, str(file_path)) from e
