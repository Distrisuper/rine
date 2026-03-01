import pytest
from fastapi import status

def test_example_flow_success(client):
    response = client.get("/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert "Example Flow" in data["message"]
