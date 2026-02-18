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

# RINE_MOCK_PRINTERS=1 (cualquier plataforma): devolver impresoras de prueba sin requerir CUPS/impresoras reales
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
    """
    Datos de prueba para desarrollo sin CUPS (Windows, Linux sin impresoras).
    _cups_unavailable: True (CUPS no se usó). _mock: True (datos simulados).
    """
    return {
        "_cups_unavailable": True,
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
        # Normalizar a lista
        if isinstance(reasons_raw, (bytes, str)):
            reasons_raw = [reasons_raw]
        elif not isinstance(reasons_raw, (list, tuple, set)):
            reasons_raw = [reasons_raw]
        # Normalizar cada elemento a str
        reasons: list[str] = []
        for r in reasons_raw:
            if isinstance(r, bytes):
                try:
                    reasons.append(r.decode("utf-8"))
                except UnicodeDecodeError:
                    reasons.append(r.decode("utf-8", errors="replace"))
            else:
                reasons.append(str(r))

        errores_detectados = [r for r in reasons if r and r != "none"]
        razones_not_ready = [r for r in errores_detectados if r in RAZONES_NOT_READY]
        # Otras razones (desconocidas o solo informativas) se reportan en detalles pero no bloquean
        otras = [r for r in errores_detectados if r not in RAZONES_NOT_READY]

        cups_state = attrs.get("printer-state")
        stopped = cups_state == CUPS_STATE_STOPPED
        # Solo las razones conocidas en RAZONES_NOT_READY marcan not_ready; razones desconocidas no bloquean
        tiene_bloqueo_conocido = bool(razones_not_ready)
        ready = not stopped and not tiene_bloqueo_conocido

        if razones_not_ready:
            razon_key = razones_not_ready[0]
        elif otras:
            razon_key = otras[0]
        else:
            razon_key = None
        razon = MAPEO_ERRORES.get(razon_key, razon_key) if razon_key else None

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
    Retorna None si la impresora no existe.
    En modo mock respeta los datos de prueba (no devuelve None por _cups_unavailable).
    """
    flota = monitorear_flota()
    if flota.get("_cups_unavailable") and not flota.get("_mock"):
        return None
    return flota.get("printers", {}).get(nombre)
