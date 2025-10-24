class LygosAPIError(Exception):
    """Exception de base pour toutes les erreurs de l'API Lygos."""
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code

# 4xx Client Errors
class BadRequestError(LygosAPIError):
    """Levée pour les erreurs 400 - Bad Request."""
    def __init__(self, message="Bad Request", status_code=400):
        super().__init__(message, status_code)

class AuthenticationError(LygosAPIError):
    """Levée pour les erreurs 401 - Unauthorized (ex: clé d'API invalide)."""
    def __init__(self, message="Authentication failed. Please check your API key.", status_code=401):
        super().__init__(message, status_code)

class PermissionDeniedError(LygosAPIError):
    """Levée pour les erreurs 403 - Forbidden."""
    def __init__(self, message="Permission denied. You do not have access to this resource.", status_code=403):
        super().__init__(message, status_code)

class NotFoundError(LygosAPIError):
    """Levée pour les erreurs 404 - Not Found."""
    def __init__(self, message="The requested resource was not found.", status_code=404):
        super().__init__(message, status_code)

class ConflictError(LygosAPIError):
    """Levée pour les erreurs 409 - Conflict."""
    def __init__(self, message="The request conflicts with the current state of the server.", status_code=409):
        super().__init__(message, status_code)

class UnprocessableEntityError(LygosAPIError):
    """Levée pour les erreurs 422 - Unprocessable Entity."""
    def __init__(self, message="The request was well-formed but contains invalid data.", status_code=422):
        super().__init__(message, status_code)

# 5xx Server Errors
class ServerError(LygosAPIError):
    """Classe de base pour les erreurs serveur 5xx."""
    def __init__(self, message="An unexpected internal server error occurred.", status_code=500):
        super().__init__(message, status_code)

class BadGatewayError(ServerError):
    """Levée pour les erreurs 502 - Bad Gateway."""
    def __init__(self, message="The server received an invalid response from an upstream server.", status_code=502):
        super().__init__(message, status_code)

class ServiceUnavailableError(ServerError):
    """Levée pour les erreurs 503 - Service Unavailable."""
    def __init__(self, message="The service is temporarily unavailable. Please try again later.", status_code=503):
        super().__init__(message, status_code)

class GatewayTimeoutError(ServerError):
    """Levée pour les erreurs 504 - Gateway Timeout."""
    def __init__(self, message="The server did not receive a timely response from an upstream server.", status_code=504):
        super().__init__(message, status_code)
