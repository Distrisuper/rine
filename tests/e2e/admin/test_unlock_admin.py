from fastapi import status

from infrastructure.config import get_settings


def test_unlock_admin_success(client, monkeypatch):
    monkeypatch.setenv("ADMIN_SECURITY_CODE", "codigo-seguro-test")
    get_settings.cache_clear()

    response = client.post("/admin/unlock", json={"security_code": "codigo-seguro-test"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"unlocked": True}

    get_settings.cache_clear()


def test_unlock_admin_invalid_code(client, monkeypatch):
    monkeypatch.setenv("ADMIN_SECURITY_CODE", "codigo-seguro-test")
    get_settings.cache_clear()

    response = client.post("/admin/unlock", json={"security_code": "codigo-incorrecto"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Código de seguridad inválido"

    get_settings.cache_clear()
