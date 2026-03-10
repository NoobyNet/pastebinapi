"""Custom domain exceptions for the Pastebin API wrapper."""


class PastebinAPIError(Exception):
    """Base exception for Pastebin API errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(PastebinAPIError):
    """Exception raised when authentication fails."""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class PasteListError(PastebinAPIError):
    """Exception raised when listing pastes fails."""
    def __init__(self, message: str = "Failed to list pastes"):
        super().__init__(message, status_code=500)


class PasteCreationError(PastebinAPIError):
    """Exception raised when creating a paste fails."""
    def __init__(self, message: str = "Failed to create paste"):
        super().__init__(message, status_code=500)


class InvalidRequestError(PastebinAPIError):
    """Exception raised when the API request is invalid."""
    def __init__(self, message: str = "Invalid API request"):
        super().__init__(message, status_code=400)
