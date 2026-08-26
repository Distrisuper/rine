import pytest
from pydantic import ValidationError
from domain.validators.print_job.label_validator import LabelPayloadValidator
from domain.validators.print_job.remito_validator import RemitoPayloadValidator
from domain.validators.print_job.s3_fricrot_validator import S3FricRotPayloadValidator
from domain.validators.print_job.payload_validator_context import PayloadValidatorContext


class TestLabelPayloadValidator:
    @pytest.fixture
    def validator(self):
        return LabelPayloadValidator()

    def test_valid_payload(self, validator):
        payload = {
            "to": "Juan Perez",
            "address": "Calle Falsa 123",
            "city": "Buenos Aires",
            "packages": "2",
            "transport": "OCA",
            "observations": "Entregar en portería"
        }
        result = validator.validate(payload)
        
        assert result["to"] == "Juan Perez"
        assert result["address"] == "Calle Falsa 123"
        assert result["city"] == "Buenos Aires"
        assert result["packages"] == "2"
        assert result["transport"] == "OCA"
        assert result["observations"] == "Entregar en portería"

    def test_missing_required_field_raises_error(self, validator):
        payload = {
            "to": "Juan Perez",
            "address": "Calle Falsa 123",
            "city": "Buenos Aires",
            "packages": "2",
            # missing "transport"
        }
        with pytest.raises(ValidationError):
            validator.validate(payload)

    def test_empty_to_raises_error(self, validator):
        payload = {
            "to": "",
            "address": "Calle Falsa 123",
            "city": "Buenos Aires",
            "packages": "2",
            "transport": "OCA"
        }
        with pytest.raises(ValidationError):
            validator.validate(payload)

    def test_packages_as_int(self, validator):
        payload = {
            "to": "Juan Perez",
            "address": "Calle Falsa 123",
            "city": "Buenos Aires",
            "packages": 5,
            "transport": "OCA"
        }
        result = validator.validate(payload)
        assert result["packages"] == 5

    def test_comentarios_alias_is_mapped_to_observations(self, validator):
        payload = {
            "to": "Juan Perez",
            "address": "Calle Falsa 123",
            "city": "Buenos Aires",
            "packages": "1",
            "transport": "OCA",
            "comentarios": "DROPSHIPPING urgente"
        }
        result = validator.validate(payload)

        assert result["observations"] == "DROPSHIPPING urgente"
        assert "comentarios" not in result

    def test_obs_alias_is_mapped_to_observations(self, validator):
        payload = {
            "to": "Juan Perez",
            "address": "Calle Falsa 123",
            "city": "Buenos Aires",
            "packages": "1",
            "transport": "OCA",
            "obs": "DROPSHIPPING urgente"
        }
        result = validator.validate(payload)

        assert result["observations"] == "DROPSHIPPING urgente"
        assert "obs" not in result

    def test_observations_takes_precedence_over_aliases(self, validator):
        payload = {
            "to": "Juan Perez",
            "address": "Calle Falsa 123",
            "city": "Buenos Aires",
            "packages": "1",
            "transport": "OCA",
            "observations": "texto real",
            "comentarios": "no debería usarse",
            "obs": "tampoco debería usarse"
        }
        result = validator.validate(payload)

        assert result["observations"] == "texto real"

    def test_no_observations_or_aliases_defaults_to_empty(self, validator):
        payload = {
            "to": "Juan Perez",
            "address": "Calle Falsa 123",
            "city": "Buenos Aires",
            "packages": "1",
            "transport": "OCA"
        }
        result = validator.validate(payload)

        assert result["observations"] == ""


class TestRemitoPayloadValidator:
    @pytest.fixture
    def validator(self):
        return RemitoPayloadValidator()

    def test_valid_payload(self, validator):
        payload = {
            "client_code": "CLIENTE001",
            "client_name": "Juan Perez",
            "order_number": "ORD-12345",
            "address": "Calle Falsa 123",
            "city": "Buenos Aires",
            "items": [
                {"codigo": "A-001", "descripcion": "Producto A", "cantidad": "2"},
                {"codigo": "B-002", "descripcion": "Producto B", "cantidad": "1"}
            ],
            "total": "1500.50",
            "remito_id": "REM-001",
            "fecha": "2024-01-15"
        }
        result = validator.validate(payload)
        
        assert result["client_code"] == "CLIENTE001"
        assert result["order_number"] == "ORD-12345"
        assert len(result["items"]) == 2
        assert result["items"][0]["codigo"] == "A-001"
        assert result["items"][0]["cantidad"] == "2"
        assert result["total"] == "1500.50"

    def test_optional_fields(self, validator):
        payload = {
            "order_number": "ORD-12345",
            "address": "Calle Falsa 123"
        }
        result = validator.validate(payload)
        
        assert result["client_code"] is None
        assert result["total"] == "0.0"
        assert result["items"] == []


class TestS3FricRotPayloadValidator:
    @pytest.fixture
    def validator(self):
        return S3FricRotPayloadValidator()

    def test_valid_payload_pdf_base64(self, validator):
        payload = {
            "pdf_base64": "SGVsbG8gV29ybGQ="
        }
        result = validator.validate(payload)
        assert result["pdf_base64"] == "SGVsbG8gV29ybGQ="

    def test_valid_payload_pdf_url(self, validator):
        payload = {
            "pdf_url": "https://example.com/file.pdf"
        }
        result = validator.validate(payload)
        assert result["pdf_url"] == "https://example.com/file.pdf"

    def test_valid_payload_ftp_filename(self, validator):
        payload = {
            "ftp_filename": "remito_123.pdf"
        }
        result = validator.validate(payload)
        assert result["ftp_filename"] == "remito_123.pdf"

    def test_valid_payload_pdf_path(self, validator):
        payload = {
            "pdf_path": "/path/to/file.pdf"
        }
        result = validator.validate(payload)
        assert result["pdf_path"] == "/path/to/file.pdf"

    def test_valid_payload_with_extra_data(self, validator):
        payload = {
            "pdf_base64": "SGVsbG8gV29ybGQ=",
            "extra_data": {"key": "value"}
        }
        result = validator.validate(payload)
        assert result["extra_data"]["key"] == "value"

    def test_missing_all_sources_raises_error(self, validator):
        payload = {
            "other_field": "some_value"
        }
        with pytest.raises(ValidationError, match="Debe proporcionar al menos una fuente de PDF"):
            validator.validate(payload)


class TestPayloadValidatorContext:
    def test_register_and_get(self):
        validator = LabelPayloadValidator()
        PayloadValidatorContext.register("TEST", validator)
        
        result = PayloadValidatorContext.get_validator("TEST")
        assert isinstance(result, LabelPayloadValidator)

    def test_get_unknown_raises_error(self):
        with pytest.raises(ValueError, match="No hay validator para document_source"):
            PayloadValidatorContext.get_validator("UNKNOWN")

    def test_validate_uses_correct_validator(self):
        PayloadValidatorContext.register("TEST_LABEL", LabelPayloadValidator())
        
        payload = {
            "to": "Juan",
            "address": "Calle 123",
            "city": "Ciudad",
            "packages": "1",
            "transport": "OCA"
        }
        result = PayloadValidatorContext.validate("TEST_LABEL", payload)
        
        assert result["to"] == "Juan"
