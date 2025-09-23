class LygosAPIError(Exception):
    """Base exception class for Lygos API errors."""
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code

# 4xx Client Errors
class BadRequestError(LygosAPIError):
    """Raised for 400 - Bad Request errors."""
    def __init__(self, message="Bad Request", status_code=400):
        super().__init__(message, status_code)

class AuthenticationError(LygosAPIError):
    """Raised for 401 - Unauthorized errors (e.g., invalid API key)."""
    def __init__(self, message="Authentication failed. Please check your API key.", status_code=401):
        super().__init__(message, status_code)

class PermissionDeniedError(LygosAPIError):
    """Raised for 403 - Forbidden errors."""
    def __init__(self, message="Permission denied. You do not have access to this resource.", status_code=403):
        super().__init__(message, status_code)

class NotFoundError(LygosAPIError):
    """Raised for 404 - Not Found errors."""
    def __init__(self, message="The requested resource was not found.", status_code=404):
        super().__init__(message, status_code)

class ConflictError(LygosAPIError):
    """Raised for 409 - Conflict errors."""
    def __init__(self, message="The request conflicts with the current state of the server.", status_code=409):
        super().__init__(message, status_code)

class UnprocessableEntityError(LygosAPIError):
    """Raised for 422 - Unprocessable Entity errors."""
    def __init__(self, message="The request was well-formed but contains invalid data.", status_code=422):
        super().__init__(message, status_code)

# 5xx Server Errors
class ServerError(LygosAPIError):
    """Base class for 5xx server errors."""
    def __init__(self, message="An unexpected internal server error occurred.", status_code=500):
        super().__init__(message, status_code)

class BadGatewayError(ServerError):
    """Raised for 502 - Bad Gateway errors."""
    def __init__(self, message="The server received an invalid response from an upstream server.", status_code=502):
        super().__init__(message, status_code)

class ServiceUnavailableError(ServerError):
    """Raised for 503 - Service Unavailable errors."""
    def __init__(self, message="The service is temporarily unavailable. Please try again later.", status_code=503):
        super().__init__(message, status_code)

class GatewayTimeoutError(ServerError):
    """Raised for 504 - Gateway Timeout errors."""
    def __init__(self, message="The server did not receive a timely response from an upstream server.", status_code=504):
        super().__init__(message, status_code)
