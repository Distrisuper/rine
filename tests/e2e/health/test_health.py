import pytest
from fastapi import status

def test_health_check_success(client):
    response = client.get("/health")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"
