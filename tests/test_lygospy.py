import pytest
from unittest.mock import patch, MagicMock
from lygospy.lygospy import Lygos
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
    GatewayTimeoutError,
)

@pytest.fixture
def lygos_client():
    """Fixture for Lygos client."""
    return Lygos(api_key="test_api_key")

def test_initialization(lygos_client):
    """Test that the Lygos client is initialized correctly."""
    assert lygos_client.api_key == "test_api_key"
    assert lygos_client.api_url == "https://api.lygosapp.com/v1/"
    assert lygos_client.headers["api-key"] == "test_api_key"

@patch('lygospy.lygospy.requests.request')
def test_successful_request(mock_request, lygos_client):
    """Test a successful API request."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_request.return_value = mock_response

    response = lygos_client._request("GET", "test_endpoint")
    assert response == {"status": "success"}
    mock_request.assert_called_once_with(
        "GET", "https://api.lygosapp.com/v1/test_endpoint", headers=lygos_client.headers
    )

@patch('lygospy.lygospy.requests.request')
def test_http_error_handling(mock_request, lygos_client):
    """Test that HTTP errors are correctly handled and mapped to custom exceptions."""
    error_map = {
        400: BadRequestError, 401: AuthenticationError, 403: PermissionDeniedError,
        404: NotFoundError, 409: ConflictError, 422: UnprocessableEntityError,
        500: ServerError, 502: BadGatewayError, 503: ServiceUnavailableError,
        504: GatewayTimeoutError, 418: LygosAPIError # I'm a teapot
    }

    for status_code, exception_class in error_map.items():
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.reason = "Test Error"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_request.return_value = mock_response

        with pytest.raises(exception_class):
            lygos_client._request("GET", f"test_{status_code}")

@patch('lygospy.lygospy.requests.request')
def test_list_gateways(mock_request, lygos_client):
    """Test listing all gateways."""
    lygos_client.list_gateways()
    mock_request.assert_called_once_with(
        "GET", "https://api.lygosapp.com/v1/gateway", headers=lygos_client.headers
    )

@patch('lygospy.lygospy.requests.request')
def test_create_single_gateway(mock_request, lygos_client):
    """Test creating a single gateway."""
    gateway_data = {"amount": 100, "shop_name": "Test Shop"}
    lygos_client.create_gateway(**gateway_data)
    # We can't assert the full json because of the dynamic uuid
    assert mock_request.call_args[1]['json']['amount'] == 100
    assert mock_request.call_args[1]['json']['shop_name'] == "Test Shop"
    assert mock_request.call_args[0][0] == "POST"

def test_create_single_gateway_missing_args(lygos_client):
    """Test ValueError for missing arguments in single gateway creation."""
    with pytest.raises(ValueError):
        lygos_client.create_gateway(amount=100)
    with pytest.raises(ValueError):
        lygos_client.create_gateway(shop_name="Test Shop")

@patch('lygospy.lygospy.requests.request')
def test_create_multiple_gateways(mock_request, lygos_client):
    """Test creating multiple gateways."""
    gateways_data = [
        {"amount": 100, "shop_name": "Shop 1"},
        {"amount": 200, "shop_name": "Shop 2"}
    ]
    lygos_client.create_gateway(multiple=True, gateways_data=gateways_data)
    assert mock_request.call_count == 2

def test_create_multiple_gateways_invalid_data(lygos_client):
    """Test ValueError for invalid data in multiple gateway creation."""
    with pytest.raises(ValueError):
        lygos_client.create_gateway(multiple=True, gateways_data="not a list")

@patch('lygospy.lygospy.requests.request')
def test_get_single_gateway(mock_request, lygos_client):
    """Test retrieving a single gateway."""
    lygos_client.get_gateway(gateway_id="gw_123")
    mock_request.assert_called_once_with(
        "GET", "https://api.lygosapp.com/v1/gateway/gw_123", headers=lygos_client.headers
    )

def test_get_single_gateway_missing_id(lygos_client):
    """Test ValueError for missing gateway_id in single gateway retrieval."""
    with pytest.raises(ValueError):
        lygos_client.get_gateway()

@patch('lygospy.lygospy.requests.request')
def test_get_multiple_gateways(mock_request, lygos_client):
    """Test retrieving multiple gateways."""
    gateway_ids = ["gw_123", "gw_456"]
    lygos_client.get_gateway(multiple=True, gateway_ids=gateway_ids)
    assert mock_request.call_count == 2

def test_get_multiple_gateways_invalid_data(lygos_client):
    """Test ValueError for invalid data in multiple gateway retrieval."""
    with pytest.raises(ValueError):
        lygos_client.get_gateway(multiple=True, gateway_ids="not a list")

@patch('lygospy.lygospy.requests.request')
def test_update_single_gateway(mock_request, lygos_client):
    """Test updating a single gateway."""
    update_data = {"message": "Updated message"}
    lygos_client.update_gateway(gateway_id="gw_123", **update_data)
    mock_request.assert_called_once_with(
        "PUT", "https://api.lygosapp.com/v1/gateway/gw_123", headers=lygos_client.headers, json=update_data
    )

def test_update_single_gateway_missing_id(lygos_client):
    """Test ValueError for missing gateway_id in single gateway update."""
    with pytest.raises(ValueError):
        lygos_client.update_gateway(message="some message")

@patch('lygospy.lygospy.requests.request')
def test_update_multiple_gateways(mock_request, lygos_client):
    """Test updating multiple gateways."""
    gateways_data = {
        "gw_123": {"message": "Hello"},
        "gw_456": {"amount": 500}
    }
    lygos_client.update_gateway(multiple=True, gateways_data=gateways_data)
    assert mock_request.call_count == 2

def test_update_multiple_gateways_invalid_data(lygos_client):
    """Test ValueError for invalid data in multiple gateway update."""
    with pytest.raises(ValueError):
        lygos_client.update_gateway(multiple=True, gateways_data="not a dict")

@patch('lygospy.lygospy.requests.request')
def test_delete_gateway(mock_request, lygos_client):
    """Test deleting a gateway."""
    lygos_client.delete_gateway(gateway_id="gw_123")
    mock_request.assert_called_once_with(
        "DELETE", "https://api.lygosapp.com/v1/gateway/gw_123", headers=lygos_client.headers
    )

@patch('lygospy.lygospy.requests.request')
def test_get_payin_status(mock_request, lygos_client):
    """Test getting payin status."""
    lygos_client.get_payin_status(order_id="order_123")
    mock_request.assert_called_once_with(
        "GET", "https://api.lygosapp.com/v1/gateway/payin/order_123", headers=lygos_client.headers
    )

@patch.object(Lygos, 'get_gateway')
def test_dynamic_get_methods(mock_get_gateway, lygos_client):
    """Test dynamic get_<field> methods."""
    mock_get_gateway.return_value = {
        "link": "https://example.com",
        "amount": 100,
        "shop_name": "Test Shop"
    }

    result = lygos_client.get_link(gateway_id="gw_123")
    assert result == {"link": "https://example.com"}
    mock_get_gateway.assert_called_with(gateway_id="gw_123")

    result = lygos_client.get_amount(gateway_id="gw_123")
    assert result == {"amount": 100}

def test_dynamic_method_attribute_error(lygos_client):
    """Test that AttributeError is raised for unsupported dynamic methods."""
    with pytest.raises(AttributeError):
        lygos_client.get_unsupported_field("gw_123")
