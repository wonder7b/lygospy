import unittest
from lygospy.error_handler import (
    LygosAPIError,
    BadRequestError,
    AuthenticationError,
    PermissionDeniedError,
    NotFoundError,
    ConflictError,
    UnprocessableEntityError,
    ServerError,
    BadGatewayError,
    ServiceUnavailableError,
    GatewayTimeoutError
)

class TestErrorHandler(unittest.TestCase):

    def test_base_exception(self):
        with self.assertRaises(LygosAPIError) as context:
            raise LygosAPIError("Base error message", 999)
        self.assertEqual(context.exception.status_code, 999)
        self.assertIn("Base error message", str(context.exception))

    def test_specific_exceptions(self):
        exceptions = [
            (BadRequestError, 400, "Bad Request"),
            (AuthenticationError, 401, "Authentication failed. Please check your API key."),
            (PermissionDeniedError, 403, "Permission denied. You do not have access to this resource."),
            (NotFoundError, 404, "The requested resource was not found."),
            (ConflictError, 409, "The request conflicts with the current state of the server."),
            (UnprocessableEntityError, 422, "The request was well-formed but contains invalid data."),
            (ServerError, 500, "An unexpected internal server error occurred."),
            (BadGatewayError, 502, "The server received an invalid response from an upstream server."),
            (ServiceUnavailableError, 503, "The service is temporarily unavailable. Please try again later."),
            (GatewayTimeoutError, 504, "The server did not receive a timely response from an upstream server."),
        ]

        for exc, code, default_message in exceptions:
            with self.subTest(exception=exc.__name__):
                # Test with default message
                with self.assertRaises(exc) as context:
                    raise exc()
                self.assertEqual(context.exception.status_code, code)
                self.assertEqual(str(context.exception), default_message)

                # Test with custom message
                custom_message = "This is a custom message"
                with self.assertRaises(exc) as context:
                    raise exc(custom_message, code)
                self.assertEqual(context.exception.status_code, code)
                self.assertEqual(str(context.exception), custom_message)

    def test_inheritance(self):
        self.assertTrue(issubclass(BadRequestError, LygosAPIError))
        self.assertTrue(issubclass(ServerError, LygosAPIError))
        self.assertTrue(issubclass(BadGatewayError, ServerError))

if __name__ == '__main__':
    unittest.main()
