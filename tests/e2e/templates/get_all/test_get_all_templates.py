import pytest
from fastapi import status
from infrastructure.repositories.template_repository import TemplateRepository
from infrastructure.db.database import engine

def test_list_templates_empty(client):
    response = client.get("/templates")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

def test_list_templates_with_data(client):
    repo = TemplateRepository(engine)
    repo.create(name="T1", file_path="t1.zpl")
    repo.create(name="T2", file_path="t2.html")
    
    response = client.get("/templates")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    names = [t["name"] for t in data]
    assert "T1" in names
    assert "T2" in names
