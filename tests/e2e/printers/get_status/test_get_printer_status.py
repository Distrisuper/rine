import pytest
from unittest.mock import patch
from fastapi import status

def test_get_flota_status_mocked(client):
    mock_status = {
        "printers": {
            "P1": {"status": "idle", "jobs": 0},
            "P2": {"status": "printing", "jobs": 1}
        }
    }
    
    with patch("infrastructure.services.printer_discovery_service.CupsPrinterDiscoveryService.get_flota_status", return_value=mock_status):
        response = client.get("/printers/status")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "P1" in data["printers"]
        assert data["printers"]["P2"]["status"] == "printing"

def test_get_one_printer_status_mocked(client):
    mock_printer = {
        "ready": True,
        "estado": "ready",
        "estado_codigo": 1,
        "razon": None,
        "detalles": [],
        "cups_state": 3,
        "modelo": "HP LaserJet 1020",
        "ocupada": False
    }
    
    with patch("infrastructure.services.printer_discovery_service.CupsPrinterDiscoveryService.get_printer_status", return_value=mock_printer):
        response = client.get("/printers/status/P1")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["ready"] is True
        assert data["estado"] == "ready"
        assert data["modelo"] == "HP LaserJet 1020"

def test_get_one_printer_status_not_found(client):
    with patch("infrastructure.services.printer_discovery_service.CupsPrinterDiscoveryService.get_printer_status", return_value=None):
        response = client.get("/printers/status/Unknown")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "no encontrada" in response.json()["detail"].lower()
