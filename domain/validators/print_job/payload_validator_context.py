from typing import Any

from domain.validators.payload_validator_interface import PayloadValidator
from domain.validators.print_job.remito_validator import RemitoPayloadValidator

class PayloadValidatorContext:
    _validators: dict[str, PayloadValidator] = {}
    
    @classmethod
    def register(cls, document_source: str, validator: PayloadValidator):
        cls._validators[document_source] = validator
    
    @classmethod
    def get_validator(cls, document_source: str) -> PayloadValidator:
        validator = cls._validators.get(document_source)
        if not validator:
            raise ValueError(f"No hay validator para document_source: {document_source}")
        return validator
    
    @classmethod
    def validate(cls, document_source: str, payload: dict[str, Any]) -> dict[str, Any]:
        validator = cls.get_validator(document_source)
        return validator.validate(payload)


def _has_nonempty_client_str(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


class PayloadValidatorResolver:
    """Resuelve qué validator usar basándose en el channel y su configuración."""
    
    def __init__(self, channel_repo):
        self._channel_repo = channel_repo
    
    def get_validator_for_channel(self, channel_number: int, session) -> PayloadValidator:
        channel = self._channel_repo.get_by_number(channel_number)
        if not channel:
            raise ValueError(f"Channel {channel_number} no existe")
        
        document_source = channel.document_source
        
        if document_source == "S3_REMITOS_FRIC_ROT":
            return PayloadValidatorContext.get_validator("S3_REMITOS_FRIC_ROT")
        
        if document_source == "INTERNAL":
            template = channel.get_template(session)
            if not template:
                raise ValueError(f"Channel {channel_number} es INTERNAL pero no tiene template")
            
            file_path = template.file_path.lower()
            if file_path.endswith('.zpl'):
                return PayloadValidatorContext.get_validator("INTERNAL_LABEL")
            if file_path.endswith('.html'):
                return PayloadValidatorContext.get_validator("INTERNAL_REMITO")
            
            raise ValueError(f"Template {file_path} no soportado. Debe ser .zpl o .html")
        
        raise ValueError(f"document_source '{document_source}' no soportado")
    
    def validate_payload(
        self,
        channel_number: int,
        payload: dict[str, Any],
        session,
        *,
        client_code: str | None = None,
        client_name: str | None = None,
    ) -> dict[str, Any]:
        working = dict(payload)
        validator = self.get_validator_for_channel(channel_number, session)
        if (
            client_code is not None
            and client_name is not None
            and isinstance(validator, RemitoPayloadValidator)
        ):
            if not _has_nonempty_client_str(working.get("client_code")):
                working["client_code"] = client_code.strip()
            if not _has_nonempty_client_str(working.get("client_name")):
                working["client_name"] = client_name.strip()
        return validator.validate(working)
