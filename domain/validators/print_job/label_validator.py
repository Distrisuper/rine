from typing import Any
from domain.validators.payload_validator_interface import PayloadValidator
from infrastructure.dtos.print_jobs.payloads.label import LabelPayloadDTO

class LabelPayloadValidator(PayloadValidator):
    def validate(self, payload: dict[str, Any]) -> dict[str, Any]:
        validated = LabelPayloadDTO(**payload)
        return validated.model_dump()
