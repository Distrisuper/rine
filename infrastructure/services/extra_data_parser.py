"""Implementación del parser de extra_data; delega en el modelo (Tell, Don't Ask)."""
from domain.services.extra_data_parser_interface import ExtraDataParser
from domain.entities.models import ExtraDataRemito


class DefaultExtraDataParser(ExtraDataParser):
    """Parsea extra_data usando ExtraDataRemito.from_json."""

    def parse(self, raw: str | None) -> ExtraDataRemito | None:
        return ExtraDataRemito.from_json(raw)
