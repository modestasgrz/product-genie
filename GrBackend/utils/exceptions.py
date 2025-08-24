class ShotCompositionException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class JSONDecodeRetranslateError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class GeminiAPIError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


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


class MeshyAIError(Exception):
    """Custom exception for Meshy AI errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class MeshyAIRequestValueError(ValueError):
    """Custom exception for Meshy AI value errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class DPressoError(Exception):
    """Custom exception for 3D Presso errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class DPressoRequestValueError(ValueError):
    """Custom exception for 3D Presso value errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class GCSExchangeError(Exception):
    """Custom exception for GCS file exchange errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
