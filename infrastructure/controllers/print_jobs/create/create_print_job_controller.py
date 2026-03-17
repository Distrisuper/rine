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
        channel: int,
        client_code: str,
        client_name: str,
        payload: dict[str, Any],
        number_of_copies: int,
        session: Session,
    ) -> dict:
        validated_payload = self._payload_validator_resolver.validate_payload(
            channel_number=channel,
            payload=payload,
            session=session,
        )
        return self._use_case(channel, client_code, client_name, validated_payload, number_of_copies)
