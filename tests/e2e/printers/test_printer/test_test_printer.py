import pytest
from fastapi import status
from sqlmodel import Session, select
from infrastructure.repositories.printer_repository import PrinterRepository
from infrastructure.repositories.channel_repository import ChannelRepository
from infrastructure.repositories.template_repository import TemplateRepository
from domain.entities.print_job import PrintJob
from infrastructure.db.database import engine

def test_printer_test_endpoint_creates_jobs(client):
    # Setup complejo: Template -> Channel -> Printer
    template_repo = TemplateRepository(engine)
    channel_repo = ChannelRepository(engine)
    printer_repo = PrinterRepository(engine)
    
    t1 = template_repo.create(name="Label", file_path="label.zpl")
    t2 = template_repo.create(name="Remito", file_path="remito.html")
    
    c1 = channel_repo.create(channel_number=1, description="C1", template_id=t1.id, document_source="INTERNAL")
    c2 = channel_repo.create(channel_number=2, description="C2", template_id=t2.id, document_source="INTERNAL")
    
    p1 = printer_repo.create_printer(name="Test Printer", channel_ids=[c1.id, c2.id])
    printer_id = p1["id"]
    
    # Ejecutar el test de la impresora (Path corregido)
    response = client.post(f"/printers/{printer_id}/test")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["printer"] == "Test Printer"
    assert len(data["jobs"]) == 2
    
    # Verificar que los trabajos se crearon en la base de datos
    with Session(engine) as session:
        jobs = session.exec(select(PrintJob)).all()
        assert len(jobs) == 2
        
        # Verificar canales
        channels_in_jobs = [j.channel for j in jobs]
        assert 1 in channels_in_jobs
        assert 2 in channels_in_jobs
        
        # Verificar estado inicial
        for job in jobs:
            assert job.status == "pending"
            assert job.payload is not None

def test_printer_test_no_channels(client):
    # Setup: Impresora sin canales
    printer_repo = PrinterRepository(engine)
    p1 = printer_repo.create_printer(name="Empty Printer", channel_ids=[])
    
    response = client.post(f"/printers/{p1['id']}/test")
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "no tiene channels" in response.json()["detail"].lower()
