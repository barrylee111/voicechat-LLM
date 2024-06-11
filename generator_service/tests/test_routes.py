import pytest

from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from ..server import app

@pytest.fixture
def api_client():
    return TestClient(app)

@patch("generator_service.routes.router")
def test_generate_response_integration(mock_generate_response, api_client):
    # Make request to the endpoint
    response = api_client.post(
        "/generate",
        json={"prompt": "Please return the answer as a one word response. What's the capital of France?"}
    )

    # Assert HTTP status code and response content
    assert response.json()['response'] == "Paris"
    assert response.status_code == 200

