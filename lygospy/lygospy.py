from .error_handler import (
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
import requests
import uuid

class Lygos:
    """
    A Python client for the Lygos API.
    
    This client supports dynamic methods for retrieving specific gateway fields.
    You can call methods like `get_link(gateway_id)`, `get_amount(gateway_id)`, etc.,
    to get a dictionary containing just the requested field.
    
    Supported fields for dynamic `get` methods:
    - link, amount, shop_name, message, user_country, creation_date,
    - order_id, success_url, failure_url
    
    Example:
        lygos = Lygos(api_key="your_api_key")
        link_info = lygos.get_link("gw_some_id")
        # Returns {'link': 'https://...'}
    """
    _supported_get_fields = [
        "link", "amount", "shop_name", "message", "user_country",
        "creation_date", "order_id", "success_url", "failure_url"
    ]

    def __init__(self, api_key: str, api_url: str = "https://api.lygosapp.com/v1/"):
        self.api_key = api_key
        self.api_url = api_url
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }

    def __getattr__(self, name):
        if name.startswith("get_") and name[4:] in self._supported_get_fields:
            field = name[4:]
            def getter(gateway_id):
                """Dynamically created method to get a specific field from a gateway."""
                gateway_data = self.get_gateway(gateway_id=gateway_id)
                return {field: gateway_data.get(field)}
            return getter
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def _request(self, method, endpoint, **kwargs):
        url = self.api_url + endpoint
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            if response.status_code == 204:
                return None
            return response.json()
        except requests.exceptions.HTTPError as err:
            status_code = err.response.status_code
            error_message = f"HTTP Error: {status_code} {err.response.reason}"
            
            error_map = {
                400: BadRequestError, 401: AuthenticationError, 403: PermissionDeniedError,
                404: NotFoundError, 409: ConflictError, 422: UnprocessableEntityError,
                500: ServerError, 502: BadGatewayError, 503: ServiceUnavailableError,
                504: GatewayTimeoutError,
            }
            exception_class = error_map.get(status_code, LygosAPIError)
            raise exception_class(error_message, status_code)
            
        except requests.exceptions.RequestException as err:
            raise LygosAPIError(f"Request Error: {err}")

    def list_gateways(self):
        """Retrieves a list of all payment gateways."""
        return self._request("GET", "gateway")

    def create_gateway(self, multiple: bool = False, gateways_data: list = None, amount: int = None, shop_name: str = None, order_id: str = None, message: str = None, success_url: str = None, failure_url: str = None):
        """Creates one or more payment gateways."""
        if multiple:
            if not isinstance(gateways_data, list):
                raise ValueError("When multiple=True, 'gateways_data' must be provided as a list of gateway dictionaries.")
            
            created_gateways = []
            for gateway_data in gateways_data:
                gateway_data.setdefault("order_id", str(uuid.uuid4()))
                created_gateways.append(self._request("POST", "gateway", json=gateway_data))
            return created_gateways
        else:
            if amount is None or shop_name is None:
                raise ValueError("For single gateway creation, 'amount' and 'shop_name' are required.")

            data = { "amount": amount, "shop_name": shop_name, "order_id": order_id or str(uuid.uuid4()) }
            if message: data["message"] = message
            if success_url: data["success_url"] = success_url
            if failure_url: data["failure_url"] = failure_url
            
            return self._request("POST", "gateway", json=data)

    def get_gateway(self, gateway_id: str = None, multiple: bool = False, gateway_ids: list = None):
        """Retrieves one or more payment gateways by their ID(s)."""
        if multiple:
            if not isinstance(gateway_ids, list):
                raise ValueError("When multiple=True, 'gateway_ids' must be provided as a list.")
            
            return [self._request("GET", f"gateway/{gid}") for gid in gateway_ids]
        else:
            if gateway_id is None:
                raise ValueError("For single gateway retrieval, 'gateway_id' is required.")
            return self._request("GET", f"gateway/{gateway_id}")

    def update_gateway(self, gateway_id: str = None, multiple: bool = False, gateways_data: dict = None, **kwargs):
        """Updates one or more payment gateways."""
        if multiple:
            if not isinstance(gateways_data, dict):
                raise ValueError("When multiple=True, 'gateways_data' must be provided as a dictionary.")
            
            return [self._request("PUT", f"gateway/{gid}", json=data) for gid, data in gateways_data.items()]
        else:
            if gateway_id is None:
                raise ValueError("For single gateway update, 'gateway_id' is required.")
            return self._request("PUT", f"gateway/{gateway_id}", json=kwargs)

    def delete_gateway(self, gateway_id: str = None, multiple: bool = False, gateway_ids: list = None):
        """Deletes a specific payment gateway."""
        if multiple:
            if not isinstance(gateway_ids, list):
                raise ValueError("When multiple=True, 'gateway_ids' must be provided as a list.")
            
            return [self._request("DELETET", f"gateway/{gid}") for gid in gateway_ids]
        else:
            if gateway_id is None:
                raise ValueError("For single gateway retrieval, 'gateway_id' is required.")
            return self._request("DELETE", f"gateway/{gateway_id}")

    def get_payin_status(self, order_id: str):
        """Retrieves the status of a specific payin transaction."""
        return self._request("GET", f"gateway/payin/{order_id}")

