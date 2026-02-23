"""Construye RemitoRenderData desde QueueItem y ExtraDataRemito (sin API externa por ahora)."""
from datetime import date

from app.interfaces.remito_data_provider import RemitoDataProvider
from app.models import ExtraDataRemito, QueueItem, RemitoRenderData


def _today_str() -> str:
    """Fecha actual en formato DD/MM/YYYY para el remito."""
    return date.today().strftime("%d/%m/%Y")


class InlineRemitoDataProvider(RemitoDataProvider):
    """Armado de datos solo desde ítem y extra_data; sin llamadas a API."""

    def get_render_data(
        self,
        item: QueueItem,
        extra: ExtraDataRemito | None,
    ) -> RemitoRenderData:
        address = (extra.label_address if extra else None) or ""
        city = (extra.label_city if extra else None) or ""
        remito_id = (
            (extra.idRemito if extra and extra.idRemito else None)
            or (extra.redi_id if extra and extra.redi_id else None)
            or str(getattr(item, "redi_id", ""))
        )
        items = []  # TODO: rellenar desde API o extra cuando exista
        total = float(item.invoice_total or 0)
        # cant_unidades se calculará cuando items esté implementado/poblado
        cant_unidades = ""
        return RemitoRenderData(
            client_name=item.client_name or "",
            client_code=item.client_code or "",
            order_number=str(item.order_number),
            address=address,
            city=city,
            items=items,
            total=total,
            remito_id=remito_id or "",
            fecha=_today_str(),
            reparto="",
            sucursal="",
            obs="",
            cant_unidades=cant_unidades,
            valor_declarado=f"$ {int(total)}" if total else "",
            numero_cot="",
            numero_cai="",
            vencimiento="",
            disclaimer="No olvides controlar la mercadería, pasados los 15 días no podremos tomar tu reclamo",
        )
