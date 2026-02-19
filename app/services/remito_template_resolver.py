"""
Resolver de template de remito según reglas legacy (server, ds, location).
Solo aplica a channel 4 y 8.
"""
from app.interfaces.remito_template_resolver import RemitoTemplateResolver
from app.models import ResolvedTemplate


class LegacyRemitoTemplateResolver(RemitoTemplateResolver):
    """Reglas C#: server, ds, sucursal → template_id."""

    def resolve(
        self,
        channel: int,
        location: str,
        server: str | None = None,
        ds: str | None = None,
    ) -> ResolvedTemplate | None:
        if channel not in (4, 8):
            return None
        template_id = self._template_id_for(location, server, ds)
        return ResolvedTemplate(template_id=template_id, output_type="pdf")

    def _template_id_for(
        self,
        location: str,
        server: str | None,
        ds: str | None,
    ) -> str:
        if ds == "remito":
            sucursal = (location or "").upper()
            if sucursal == "MDP":
                return "templateremnooficialMDP"
            if sucursal == "BA":
                return "templateremnooficialBA"
            if sucursal == "ROS":
                return "templateremnooficialROS"
            return "templateremnooficialPICO"
        if ds == "1":
            return "templateds"
        if (location or "").upper() == "ROS":
            return "templateros"
        if server == "1":
            return "template"
        return "templatedimes"
