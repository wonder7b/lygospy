import pytest
from unittest.mock import patch, MagicMock
import requests.exceptions

# Import from package root thanks to __init__.py
from lygospy import Lygos
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
    assert lygos_client.base_url == "https://api.lygosapp.com/v1/"
    assert lygos_client.session.headers["api-key"] == "test_api_key"
    assert lygos_client.session.headers["User-Agent"] == "Lygos-Python-Client-v1"

def test_initialization_no_api_key():
    """Test that ValueError is raised if no API key is provided."""
    with pytest.raises(ValueError, match="Une 'api_key' est requise"):
        Lygos(api_key="")

@patch('requests.Session.request')
def test_successful_request(mock_request, lygos_client):
    """Test a successful API request."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_request.return_value = mock_response

    response = lygos_client._request("GET", "test_endpoint")
    assert response == {"status": "success"}
    mock_request.assert_called_once_with(
        "GET", "https://api.lygosapp.com/v1/test_endpoint"
    )

@patch('requests.Session.request')
def test_successful_no_content_request(mock_request, lygos_client):
    """Test a successful 204 No Content request."""
    mock_response = MagicMock()
    mock_response.status_code = 204
    mock_request.return_value = mock_response

    response = lygos_client._request("DELETE", "test_endpoint")
    assert response is None
    mock_request.assert_called_once_with(
        "DELETE", "https://api.lygosapp.com/v1/test_endpoint"
    )

@patch('requests.Session.request')
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
        mock_response.text = "Test Error Body"
        # Mock the JSONDecodeError
        mock_response.json.side_effect = requests.JSONDecodeError("msg", "doc", 0)
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_request.return_value = mock_response

        with pytest.raises(exception_class) as exc_info:
            lygos_client._request("GET", f"test_{status_code}")
        
        assert exc_info.value.status_code == status_code
        assert "Test Error Body" in str(exc_info.value)

@patch('requests.Session.request')
def test_http_error_handling_with_json_message(mock_request, lygos_client):
    """Test that HTTP errors use the JSON message field if available."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.reason = "Not Found"
    mock_response.json.return_value = {"message": "Resource not available", "details": "The ID was wrong"}
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
    mock_request.return_value = mock_response

    with pytest.raises(NotFoundError) as exc_info:
        lygos_client._request("GET", "test_404")
    
    assert exc_info.value.status_code == 404
    assert "Resource not available: The ID was wrong" in str(exc_info.value)

@patch('requests.Session.request')
def test_list_gateways(mock_request, lygos_client):
    """Test listing all gateways."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"id": "gw_1"}, {"id": "gw_2"}]
    mock_request.return_value = mock_response
    
    result = lygos_client.list_gateways()
    assert result == [{"id": "gw_1"}, {"id": "gw_2"}]
    mock_request.assert_called_once_with(
        "GET", "https://api.lygosapp.com/v1/gateway"
    )

@patch('requests.Session.request')
def test_create_single_gateway(mock_request, lygos_client):
    """Test creating a single gateway."""
    gateway_data = {"amount": 100, "shop_name": "Test Shop"}
    lygos_client.create_gateway(**gateway_data)
    
    # We can't assert the full json because of the dynamic uuid
    assert mock_request.call_args[1]['json']['amount'] == 100
    assert mock_request.call_args[1]['json']['shop_name'] == "Test Shop"
    assert "order_id" in mock_request.call_args[1]['json']
    assert mock_request.call_args[0][0] == "POST"

@patch('requests.Session.request')
def test_create_single_gateway_with_options(mock_request, lygos_client):
    """Test creating a single gateway with all optional fields."""
    gateway_data = {
        "amount": 100, 
        "shop_name": "Test Shop", 
        "order_id": "custom_order_123",
        "message": "Test Message",
        "success_url": "https://success.com",
        "failure_url": "https://failure.com"
    }
    lygos_client.create_gateway(**gateway_data)
    
    assert mock_request.call_args[1]['json'] == gateway_data
    assert mock_request.call_args[0][0] == "POST"

@patch('requests.Session.request')
def test_create_gateways_batch(mock_request, lygos_client):
    """Test creating multiple gateways using create_gateways_batch."""
    gateways_data = [
        {"amount": 100, "shop_name": "Shop 1"},
        {"amount": 200, "shop_name": "Shop 2"}
    ]
    lygos_client.create_gateways_batch(gateways_data=gateways_data)
    assert mock_request.call_count == 2
    assert mock_request.call_args_list[0][1]['json']['amount'] == 100
    assert mock_request.call_args_list[1][1]['json']['amount'] == 200

@patch('requests.Session.request')
def test_create_gateways_batch_with_failures(mock_request, lygos_client):
    """Test that batch creation continues even if one request fails."""
    mock_response_success = MagicMock()
    mock_response_success.status_code = 200
    mock_response_success.json.return_value = {"id": "gw_1", "amount": 100}
    
    mock_response_fail = MagicMock()
    mock_response_fail.status_code = 400
    mock_response_fail.reason = "Bad Data"
    mock_response_fail.text = "Bad Data"
    mock_response_fail.json.side_effect = requests.JSONDecodeError("msg", "doc", 0)
    mock_response_fail.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response_fail)
    
    mock_request.side_effect = [mock_response_success, mock_response_fail]
    
    gateways_data = [
        {"amount": 100, "shop_name": "Shop 1"},
        {"amount": 200, "shop_name": "Shop 2"}
    ]
    results = lygos_client.create_gateways_batch(gateways_data)
    
    assert mock_request.call_count == 2
    assert results[0] == {"id": "gw_1", "amount": 100}
    assert "error" in results[1]
    assert "Bad Data" in results[1]["error"]
    assert results[1]["data"]["amount"] == 200

@patch('requests.Session.request')
def test_get_single_gateway(mock_request, lygos_client):
    """Test retrieving a single gateway."""
    lygos_client.get_gateway(gateway_id="gw_123")
    mock_request.assert_called_once_with(
        "GET", "https://api.lygosapp.com/v1/gateway/gw_123"
    )

@patch('requests.Session.request')
def test_get_gateways_batch(mock_request, lygos_client):
    """Test retrieving multiple gateways using get_gateways_batch."""
    gateway_ids = ["gw_123", "gw_456"]
    lygos_client.get_gateways_batch(gateway_ids=gateway_ids)
    assert mock_request.call_count == 2
    assert mock_request.call_args_list[0][0][0] == "GET"
    assert mock_request.call_args_list[0][0][1] == "https://api.lygosapp.com/v1/gateway/gw_123"
    assert mock_request.call_args_list[1][0][1] == "https://api.lygosapp.com/v1/gateway/gw_456"

@patch('requests.Session.request')
def test_update_single_gateway(mock_request, lygos_client):
    """Test updating a single gateway."""
    update_data = {"message": "Updated message"}
    lygos_client.update_gateway(gateway_id="gw_123", **update_data)
    mock_request.assert_called_once_with(
        "PUT", "https://api.lygosapp.com/v1/gateway/gw_123", json=update_data
    )

def test_update_single_gateway_no_data(lygos_client):
    """Test ValueError for missing update data in single gateway update."""
    with pytest.raises(ValueError, match="Aucune donnée de mise à jour"):
        lygos_client.update_gateway(gateway_id="gw_123")

@patch('requests.Session.request')
def test_update_gateways_batch(mock_request, lygos_client):
    """Test updating multiple gateways using update_gateways_batch."""
    gateways_data = {
        "gw_123": {"message": "Hello"},
        "gw_456": {"amount": 500}
    }
    lygos_client.update_gateways_batch(gateways_data=gateways_data)
    assert mock_request.call_count == 2
    assert mock_request.call_args_list[0][1]['json'] == {"message": "Hello"}
    assert mock_request.call_args_list[1][1]['json'] == {"amount": 500}

@patch('requests.Session.request')
def test_delete_gateway(mock_request, lygos_client):
    """Test deleting a single gateway."""
    mock_response = MagicMock()
    mock_response.status_code = 204
    mock_request.return_value = mock_response
    
    result = lygos_client.delete_gateway(gateway_id="gw_123")
    assert result is None
    mock_request.assert_called_once_with(
        "DELETE", "https://api.lygosapp.com/v1/gateway/gw_123"
    )

@patch('requests.Session.request')
def test_delete_gateways_batch(mock_request, lygos_client):
    """Test deleting multiple gateways using delete_gateways_batch."""
    mock_response = MagicMock()
    mock_response.status_code = 204
    mock_request.return_value = mock_response

    gateway_ids = ["gw_123", "gw_456"]
    results = lygos_client.delete_gateways_batch(gateway_ids=gateway_ids)
    
    assert results == [None, None]
    assert mock_request.call_count == 2
    assert mock_request.call_args_list[0][0][0] == "DELETE"
    assert mock_request.call_args_list[0][0][1] == "https://api.lygosapp.com/v1/gateway/gw_123"
    assert mock_request.call_args_list[1][0][1] == "https://api.lygosapp.com/v1/gateway/gw_456"

@patch('requests.Session.request')
def test_get_payin_status(mock_request, lygos_client):
    """Test getting payin status."""
    lygos_client.get_payin_status(order_id="order_123")
    mock_request.assert_called_once_with(
        "GET", "https://api.lygosapp.com/v1/gateway/payin/order_123"
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
