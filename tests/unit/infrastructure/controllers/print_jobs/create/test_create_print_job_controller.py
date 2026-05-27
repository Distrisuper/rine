import pytest
from unittest.mock import Mock

from infrastructure.controllers.print_jobs.create.create_print_job_controller import (
    CreatePrintJobController,
)


def build_controller() -> tuple[CreatePrintJobController, Mock, Mock]:
    use_case = Mock()
    payload_validator_resolver = Mock()
    payload_validator_resolver.validate_payload.return_value = {"normalized": True}

    controller = CreatePrintJobController(
        use_case=use_case,
        payload_validator_resolver=payload_validator_resolver,
    )
    return controller, use_case, payload_validator_resolver


def test_create_print_job_controller_validates_types_before_processing() -> None:
    controller, use_case, payload_validator_resolver = build_controller()
    fake_session = object()

    with pytest.raises(ValueError, match="channel debe ser numerico"):
        controller(
            channel="abc",
            client_code="CL001",
            client_name="Cliente Test",
            payload={"to": "Juan"},
            number_of_copies="1",
            session=fake_session,
        )

    payload_validator_resolver.validate_payload.assert_not_called()
    use_case.assert_not_called()


def test_create_print_job_controller_validates_payload_type_before_processing() -> None:
    controller, use_case, payload_validator_resolver = build_controller()
    fake_session = object()

    with pytest.raises(ValueError, match="payload debe ser un objeto JSON"):
        controller(
            channel="1",
            client_code="CL001",
            client_name="Cliente Test",
            payload=["invalid"],
            number_of_copies="1",
            session=fake_session,
        )

    payload_validator_resolver.validate_payload.assert_not_called()
    use_case.assert_not_called()


def test_create_print_job_controller_validates_number_of_copies_string_numeric() -> None:
    controller, use_case, payload_validator_resolver = build_controller()
    fake_session = object()

    with pytest.raises(ValueError, match="number_of_copies debe ser numerico"):
        controller(
            channel="1",
            client_code="CL001",
            client_name="Cliente Test",
            payload={"to": "Juan"},
            number_of_copies="abc",
            session=fake_session,
        )

    payload_validator_resolver.validate_payload.assert_not_called()
    use_case.assert_not_called()


def test_create_print_job_controller_success_calls_resolver_and_use_case() -> None:
    controller, use_case, payload_validator_resolver = build_controller()
    fake_session = object()

    controller(
        channel="1",
        client_code="CL001",
        client_name="Cliente Test",
        payload={"to": "Juan"},
        number_of_copies="1",
        session=fake_session,
    )

    payload_validator_resolver.validate_payload.assert_called_once_with(
        channel_number=1,
        payload={"to": "Juan"},
        session=fake_session,
    )
    use_case.assert_called_once_with(
        1,
        "CL001",
        "Cliente Test",
        {"normalized": True},
        1,
    )
