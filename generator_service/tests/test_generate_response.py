import json
import pytest
from unittest.mock import MagicMock, AsyncMock

from ..old_routes import generate_response

@pytest.mark.asyncio
async def test_generate_response_valid_prompt():
    # Mock request object
    request = MagicMock()
    request.json = AsyncMock(return_value={
        "prompt": "Please return the answer as a one word response. What's the capital of France?"
    })

    # Call the handler function
    response = await generate_response(request)
    
    response_body = response.body.decode("utf-8")  # Decode the bytes to string
    response_data = json.loads(response_body)

    # Assertions
    assert response_data['response'] == 'Paris'
    assert response.status_code == 200
