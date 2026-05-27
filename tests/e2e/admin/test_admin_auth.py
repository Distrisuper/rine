import pytest
from fastapi.testclient import TestClient
from infrastructure.config import get_settings


def test_admin_requires_auth(client: TestClient):
    response = client.get("/admin/")
    assert response.status_code == 401


def test_docs_requires_auth(client: TestClient):
    response = client.get("/docs")
    assert response.status_code == 401


def test_admin_invalid_credentials(client: TestClient):
    response = client.get("/admin/", auth=("admin", "wrong_password"))
    assert response.status_code == 401


def test_docs_invalid_credentials(client: TestClient):
    response = client.get("/docs", auth=("admin", "wrong_password"))
    assert response.status_code == 401


def test_admin_valid_credentials(client: TestClient, monkeypatch):
    monkeypatch.setenv("ADMIN_USERNAME", "testuser")
    monkeypatch.setenv("ADMIN_SECURITY_CODE", "testpass")
    get_settings.cache_clear()

    response = client.get("/admin/", auth=("testuser", "testpass"))
    assert response.status_code == 200


def test_docs_valid_credentials(client: TestClient, monkeypatch):
    monkeypatch.setenv("ADMIN_USERNAME", "testuser")
    monkeypatch.setenv("ADMIN_SECURITY_CODE", "testpass")
    get_settings.cache_clear()

    response = client.get("/docs", auth=("testuser", "testpass"))
    assert response.status_code == 200


def test_public_routes_no_auth(client: TestClient):
    assert client.get("/health").status_code == 200
    assert client.get("/channels").status_code == 200
    assert client.get("/printers").status_code == 200
