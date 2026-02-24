"""Resolver de template de etiqueta/rótulo (channel 3)."""
from domain.repositories.label_template_resolver import LabelTemplateResolver
from domain.entities.models import ResolvedTemplate


class LegacyLabelTemplateResolver(LabelTemplateResolver):
    """Channel 3 → template de etiqueta estándar."""

    def resolve(self, channel: int, location: str = "") -> ResolvedTemplate | None:
        if channel != 3:
            return None
        return ResolvedTemplate(template_id="etiqueta_standard", output_type="zpl")
