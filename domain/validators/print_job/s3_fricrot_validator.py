from typing import Any
from domain.validators.payload_validator_interface import PayloadValidator
from infrastructure.dtos.print_jobs.payloads.s3_fricrot import S3FricRotPayloadDTO

class S3FricRotPayloadValidator(PayloadValidator):
    def validate(self, payload: dict[str, Any]) -> dict[str, Any]:
        validated = S3FricRotPayloadDTO(**payload)
        return validated.model_dump()
