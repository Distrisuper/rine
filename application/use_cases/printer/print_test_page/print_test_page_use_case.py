import json
import random
from typing import Any, Dict
from application.use_cases.printer.print_test_page.print_test_page_use_case_interface import PrintTestPageUseCaseInterface
from domain.repositories.printer_repository_interface import PrinterRepositoryInterface
from domain.repositories.channel_repository_interface import ChannelRepositoryInterface
from domain.repositories.template_repository_interface import TemplateRepositoryInterface
from domain.repositories.print_job_repository_interface import PrintJobRepositoryInterface
from domain.entities.print_job import PrintJob

class PrintTestPageUseCase(PrintTestPageUseCaseInterface):
    def __init__(
        self,
        printer_repo: PrinterRepositoryInterface,
        channel_repo: ChannelRepositoryInterface,
        template_repo: TemplateRepositoryInterface,
        print_job_repo: PrintJobRepositoryInterface
    ):
        self._printer_repo = printer_repo
        self._channel_repo = channel_repo
        self._template_repo = template_repo
        self._print_job_repo = print_job_repo

    def __call__(self, printer_id: int) -> dict:
        printer = self._printer_repo.get_printer_by_id(printer_id)
        if not printer:
            raise ValueError("Impresora no encontrada")

        channels = self._printer_repo.get_printer_channels(printer_id)
        if not channels:
            raise ValueError("La impresora no tiene channels configurados")

        created_jobs = []

        for ch in channels:
            channel_obj = self._channel_repo.get_by_id(ch["channel_id"])
            if not channel_obj or not channel_obj.template_id:
                continue

            template = self._template_repo.get_by_id(channel_obj.template_id)
            if not template:
                continue

            payload = self._generate_test_payload(template.file_path)
            if not payload:
                continue

            job = PrintJob(
                client_code=payload.get("client_code", "TEST"),
                client_name=payload.get("client_name", "Test Cliente"),
                channel=ch["channel_number"],
                payload=json.dumps(payload),
                status="pending",
                number_of_copies=1,
                attempt_count=0,
            )
            
            saved_job = self._print_job_repo.create(job)
            
            created_jobs.append({
                "id": saved_job.id,
                "channel": ch["channel_number"],
                "template": template.name,
                "status": saved_job.status,
            })

        return {"printer": printer.name, "jobs": created_jobs}

    def _generate_test_payload(self, file_path: str) -> Dict[str, Any]:
        file_path_lower = file_path.lower()
        if file_path_lower.endswith(".zpl"):
            return {
                "to": f"Test Destinatario {random.randint(1000, 9999)}",
                "address": f"Test Dirección {random.randint(100, 999)}",
                "city": "Test Ciudad",
                "packages": f"{random.randint(1, 5)} bulto(s)",
            }
        elif file_path_lower.endswith(".html"):
            return {
                "client_code": f"{random.randint(100, 999)}",
                "client_name": "Test Cliente S.A.",
                "order_number": random.randint(1000, 9999),
                "address": f"Test Dirección {random.randint(100, 999)}",
                "city": "Test Ciudad",
                "items": [
                    {"codigo": "TEST001", "cantidad": random.randint(1, 10), "descripcion": "Producto de prueba"},
                    {"codigo": "TEST002", "cantidad": random.randint(1, 5), "descripcion": "Otro producto"},
                ],
                "total": round(random.uniform(100, 5000), 2),
                "remito_id": f"R-TEST-{random.randint(100000, 999999)}",
                "fecha": "27/02/2026",
                "reparto": "Test Reparto",
                "sucursal": "001",
                "obs": "Trabajo de prueba",
                "cant_unidades": str(random.randint(1, 20)),
                "valor_declarado": f"${random.randint(100, 5000)}",
                "numero_cot": f"COT-{random.randint(10000, 99999)}",
                "numero_cai": f"CAI-{random.randint(10000, 99999)}",
                "vencimiento": "15/03/2026",
                "disclaimer": "Trabajo de prueba generado desde admin",
            }
        return {}
