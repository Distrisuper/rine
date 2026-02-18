"""
Detección y monitoreo de impresoras vía CUPS.
Expone estado por impresora: ready/not_ready, razones y códigos numéricos.

Códigos numéricos en la respuesta:
- estado_codigo: 1 = lista para imprimir, 0 = no lista (falla o error).
- cups_state (IPP): 3 = idle, 4 = printing, 5 = stopped.

Tipos soportados cuando la impresora está en CUPS:
- Láser: papel, tóner, puerta, etc. (paper-*, toner-*, door-open, cover-open).
- Zebra / etiquetas con ribbon: medio (media-*), insumo/ribbon (marker-supply-*).
  Si la Zebra se usa por ZPL directo (USB/serial/socket) sin CUPS, no aparece aquí.
"""
from __future__ import annotations

import os
from typing import Any

# En Windows: poner RINE_MOCK_PRINTERS=1 para devolver impresoras de prueba
def _mock_impresoras_habilitado() -> bool:
    return os.environ.get("RINE_MOCK_PRINTERS", "").strip().lower() in ("1", "true", "yes")

# CUPS solo disponible en Linux (pycups); en Windows no está
try:
    import cups  # type: ignore[import-untyped]
    CUPS_AVAILABLE = True
except ImportError:
    cups = None  # type: ignore
    CUPS_AVAILABLE = False


# Razones de CUPS que indican que la impresora NO está lista para imprimir.
# Incluye: láser (toner, paper, door), Zebra/etiquetas (media, marker-supply = ribbon/insumo).
RAZONES_NOT_READY = frozenset({
    # Papel / medio (láser y etiquetas)
    "media-empty", "media-needed", "paper-empty", "paper-needed",
    # Láser
    "toner-low", "toner-empty", "door-open", "cover-open",
    # Estado general
    "offline", "stopped", "printer-error", "paused",
    # Insumo genérico (Zebra: ribbon; láser: a veces tóner)
    "marker-supply-low", "marker-supply-empty",
    # Variantes que algunos drivers (Zebra/etiquetas) pueden reportar
    "ribbon-low", "ribbon-empty", "label-empty", "labels-needed",
})

# Mensajes legibles para razones técnicas de CUPS
MAPEO_ERRORES: dict[str, str] = {
    "media-empty": "Sin papel/medio",
    "media-needed": "Medio requerido",
    "paper-empty": "Sin papel",
    "paper-needed": "Papel requerido",
    "toner-low": "Tóner bajo",
    "toner-empty": "Sin tóner",
    "door-open": "Puerta abierta",
    "cover-open": "Tapa abierta",
    "offline": "Impresora desconectada",
    "stopped": "Impresora detenida",
    "printer-error": "Error de impresora",
    "paused": "Impresora en pausa",
    "marker-supply-low": "Insumo bajo",
    "marker-supply-empty": "Sin insumo",
    "ribbon-low": "Ribbon bajo",
    "ribbon-empty": "Sin ribbon",
    "label-empty": "Sin etiquetas",
    "labels-needed": "Etiquetas requeridas",
}

# Códigos numéricos de estado (IPP / CUPS)
# printer-state: 3=idle, 4=printing, 5=stopped
CUPS_STATE_IDLE = 3
CUPS_STATE_PRINTING = 4
CUPS_STATE_STOPPED = 5

# Estado resumido para la API: 1=lista para imprimir, 0=no lista
ESTADO_CODIGO_READY = 1
ESTADO_CODIGO_NOT_READY = 0


def _respuesta_mock_flota() -> dict[str, Any]:
    """Datos de prueba para desarrollo en Windows (sin CUPS)."""
    return {
        "_cups_unavailable": False,
        "_mock": True,
        "printers": {
            "PC42t": {
                "ready": True,
                "estado": "ready",
                "estado_codigo": ESTADO_CODIGO_READY,
                "razon": None,
                "detalles": [],
                "cups_state": CUPS_STATE_IDLE,
                "modelo": "Honeywell PC42t (etiquetas)",
                "ocupada": False,
            },
            "LaserOficina": {
                "ready": False,
                "estado": "not_ready",
                "estado_codigo": ESTADO_CODIGO_NOT_READY,
                "razon": "Sin papel",
                "detalles": ["paper-empty"],
                "cups_state": CUPS_STATE_STOPPED,
                "modelo": "HP LaserJet (genérico)",
                "ocupada": False,
            },
        },
    }


def monitorear_flota() -> dict[str, Any]:
    """
    Obtiene el estado de todas las impresoras vía CUPS.
    Devuelve un diccionario por impresora con ready/not_ready y detalles.
    En entornos sin CUPS (ej. Windows) devuelve {"_cups_unavailable": True, "printers": {}}.
    Con RINE_MOCK_PRINTERS=1 en Windows devuelve impresoras de prueba para probar la interfaz.
    """
    if not CUPS_AVAILABLE:
        if _mock_impresoras_habilitado():
            return _respuesta_mock_flota()
        return {
            "_cups_unavailable": True,
            "message": "CUPS no disponible (solo en Linux)",
            "printers": {},
        }

    conn = cups.Connection()
    printers = conn.getPrinters()
    result: dict[str, Any] = {"_cups_unavailable": False, "printers": {}}

    for name, info in printers.items():
        try:
            attrs = conn.getPrinterAttributes(name)
        except Exception as e:
            result["printers"][name] = {
                "ready": False,
                "estado": "not_ready",
                "estado_codigo": ESTADO_CODIGO_NOT_READY,
                "razon": f"Error al leer atributos: {e}",
                "detalles": [],
                "cups_state": None,
                "modelo": info.get("printer-make-and-model", "Desconocida"),
                "ocupada": False,
            }
            continue

        reasons_raw = attrs.get("printer-state-reasons") or ["none"]
        if isinstance(reasons_raw, (bytes, str)):
            reasons_raw = [reasons_raw] if isinstance(reasons_raw, str) else [reasons_raw.decode("utf-8")]
        reasons = [r if isinstance(r, str) else str(r) for r in reasons_raw]

        errores_detectados = [r for r in reasons if r and r != "none"]
        razones_not_ready = [r for r in errores_detectados if r in RAZONES_NOT_READY]
        # Cualquier razón desconocida también la consideramos "not ready" por seguridad
        otras = [r for r in errores_detectados if r not in RAZONES_NOT_READY]
        todas_not_ready = razones_not_ready or otras

        cups_state = attrs.get("printer-state")
        stopped = cups_state == CUPS_STATE_STOPPED
        ready = not stopped and not todas_not_ready

        if todas_not_ready:
            razon = MAPEO_ERRORES.get(todas_not_ready[0], todas_not_ready[0])
        else:
            razon = None

        result["printers"][name] = {
            "ready": ready,
            "estado": "ready" if ready else "not_ready",
            "estado_codigo": ESTADO_CODIGO_READY if ready else ESTADO_CODIGO_NOT_READY,  # 1=ready, 0=not_ready
            "razon": razon,
            "detalles": errores_detectados,
            "cups_state": cups_state,  # IPP: 3=idle, 4=printing, 5=stopped
            "modelo": attrs.get("printer-make-and-model") or info.get("printer-make-and-model", "Genérica"),
            "ocupada": cups_state == CUPS_STATE_PRINTING,
        }

    return result


def estado_impresora(nombre: str) -> dict[str, Any] | None:
    """
    Estado de una sola impresora por nombre.
    Retorna None si la impresora no existe o CUPS no está disponible.
    """
    flota = monitorear_flota()
    if flota.get("_cups_unavailable"):
        return None
    return flota.get("printers", {}).get(nombre)
