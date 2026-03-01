import pytest
from unittest.mock import patch
from fastapi import status

def test_discover_printers_mocked(client):
    mock_data = [
        {"name": "Mock Printer 1", "model": "Model X", "type": "laser_printer"},
        {"name": "Mock Zebra 1", "model": "Model Z", "type": "zebra_printer"},
    ]
    
    with patch("infrastructure.services.printer_discovery_service.CupsPrinterDiscoveryService.discover_printers", return_value=mock_data):
        response = client.get("/printers/discover")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Mock Printer 1"
        assert data[1]["type"] == "zebra_printer"
