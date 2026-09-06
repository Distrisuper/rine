from typing import Any
from domain.validators.payload_validator_interface import PayloadValidator
from infrastructure.dtos.print_jobs.payloads.remito import RemitoPayloadDTO

class RemitoPayloadValidator(PayloadValidator):
    def validate(self, payload: dict[str, Any]) -> dict[str, Any]:
        validated = RemitoPayloadDTO(**payload)
        return validated.model_dump(exclude_none=True)
