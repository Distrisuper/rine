from typing import Any
from sqlmodel import Session
from application.use_cases.print_jobs.create.create_print_job_use_case import CreatePrintJobUseCase
from domain.validators.print_job.payload_validator_context import PayloadValidatorResolver


class CreatePrintJobController:
    def __init__(
        self,
        use_case: CreatePrintJobUseCase,
        payload_validator_resolver: PayloadValidatorResolver,
    ):
        self._use_case = use_case
        self._payload_validator_resolver = payload_validator_resolver

    def __call__(
        self,
        channel: str,
        client_code: str,
        client_name: str,
        payload: dict[str, Any],
        number_of_copies: str,
        session: Session,
    ) -> dict:
        parsed_channel, parsed_number_of_copies = self._validate_input_types(
            channel=channel,
            client_code=client_code,
            client_name=client_name,
            payload=payload,
            number_of_copies=number_of_copies,
        )
        validated_payload = self._payload_validator_resolver.validate_payload(
            channel_number=parsed_channel,
            payload=payload,
            session=session,
        )
        return self._use_case(
            parsed_channel,
            client_code,
            client_name,
            validated_payload,
            parsed_number_of_copies,
        )

    def _validate_input_types(
        self,
        channel: Any,
        client_code: Any,
        client_name: Any,
        payload: Any,
        number_of_copies: Any,
    ) -> tuple[int, int]:
        """Valida entrada string y devuelve valores parseados para dominio."""
        if not isinstance(channel, str):
            raise ValueError("channel debe ser string")
        if not channel.strip():
            raise ValueError("channel no puede estar vacio")
        if not channel.strip().isdigit():
            raise ValueError("channel debe ser numerico")

        parsed_channel = int(channel.strip())
        if parsed_channel <= 0:
            raise ValueError("channel debe ser mayor a 0")

        if not isinstance(client_code, str):
            raise ValueError("client_code debe ser str")
        if not client_code.strip():
            raise ValueError("client_code no puede estar vacio")

        if not isinstance(client_name, str):
            raise ValueError("client_name debe ser str")
        if not client_name.strip():
            raise ValueError("client_name no puede estar vacio")

        if not isinstance(payload, dict):
            raise ValueError("payload debe ser un objeto JSON")

        if number_of_copies is None:
            number_of_copies = "1"
        if not isinstance(number_of_copies, str):
            raise ValueError("number_of_copies debe ser string")
        if not number_of_copies.strip():
            raise ValueError("number_of_copies no puede estar vacio")
        if not number_of_copies.strip().isdigit():
            raise ValueError("number_of_copies debe ser numerico")

        parsed_number_of_copies = int(number_of_copies.strip())
        if parsed_number_of_copies < 1:
            raise ValueError("number_of_copies debe ser mayor o igual a 1")
        if parsed_number_of_copies > 100:
            raise ValueError("number_of_copies debe ser menor o igual a 100")

        return parsed_channel, parsed_number_of_copies
