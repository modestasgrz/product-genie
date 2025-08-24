class BlenderProcessError(Exception):
    """Custom exception for Blender process errors."""

    def __init__(self, message: str, return_code: int | None = None) -> None:
        super().__init__(message)
        self.return_code = return_code


class FileHandlerError(Exception):
    """Custom exception for file handler operations."""

    def __init__(self, message: str, file_path: str | None = None) -> None:
        super().__init__(message)
        self.file_path = file_path
