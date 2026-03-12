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

import logging
import os
from typing import Any

from domain.services.printer_discovery_interface import PrinterDiscovery

logger = logging.getLogger(__name__)

# RINE_MOCK_PRINTERS=1 (cualquier plataforma): devolver impresoras de prueba sin requerir CUPS/impresoras reales
def _mock_impresoras_habilitado() -> bool:
    return os.environ.get("RINE_MOCK_PRINTERS", "").strip().lower() in ("1", "true", "yes")

# CUPS solo disponible en Linux (pycups); en Windows no está
try:
    import cups  # type: ignore[import-untyped]
    CUPS_AVAILABLE = True
    # Configurar servidor remoto si existe la variable
    cups_server = os.getenv("CUPS_SERVER")
    if cups_server:
        cups.setServer(cups_server)
        # Forzar encriptación desactivada para evitar Bad Request (1024)
        cups.setEncryption(cups.HTTP_ENCRYPT_NEVER)
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


def _estado_desde_atributos(attrs: dict[str, Any], modelo_fallback: str = "Genérica") -> dict[str, Any]:
    """
    Construye el diccionario de estado de una impresora a partir de atributos IPP/CUPS.
    Misma estructura que los valores de `printers` en monitorear_flota y _respuesta_mock_flota.
    """
    reasons_raw = attrs.get("printer-state-reasons") or ["none"]
    if isinstance(reasons_raw, (bytes, str)):
        reasons_raw = [reasons_raw]
    elif not isinstance(reasons_raw, (list, tuple, set)):
        reasons_raw = [reasons_raw]
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
    otras = [r for r in errores_detectados if r not in RAZONES_NOT_READY]

    cups_state = attrs.get("printer-state")
    stopped = cups_state == CUPS_STATE_STOPPED
    tiene_bloqueo_conocido = bool(razones_not_ready)
    ready = not stopped and not tiene_bloqueo_conocido

    if razones_not_ready:
        razon_key = razones_not_ready[0]
    elif otras:
        razon_key = otras[0]
    else:
        razon_key = None
    razon = MAPEO_ERRORES.get(razon_key, razon_key) if razon_key else None

    return {
        "ready": ready,
        "estado": "ready" if ready else "not_ready",
        "estado_codigo": ESTADO_CODIGO_READY if ready else ESTADO_CODIGO_NOT_READY,
        "razon": razon,
        "detalles": errores_detectados,
        "cups_state": cups_state,
        "modelo": attrs.get("printer-make-and-model") or attrs.get("printer-info") or modelo_fallback,
        "ocupada": cups_state == CUPS_STATE_PRINTING,
    }


def _detectar_tipo_impresora(modelo: str) -> str:
    """Detecta el tipo de impresora (zebra/laser) basándose en el modelo."""
    modelo_lower = modelo.lower()
    keywords_zebra = ["zebra", "label", "etiqueta", "zpl", "honeywell", "datamax", "tsc", "golio"]
    if any(k in modelo_lower for k in keywords_zebra):
        return "zebra"
    return "laser"


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

    try:
        conn = cups.Connection()
        printers = conn.getPrinters()
    except Exception as e:
        logger.exception("CUPS no accesible")
        if _mock_impresoras_habilitado():
            return _respuesta_mock_flota()
        return {
            "_cups_unavailable": True,
            "message": "CUPS no accesible",
            "printers": {},
        }

    result: dict[str, Any] = {"_cups_unavailable": False, "printers": {}}

    for name, info in printers.items():
        try:
            attrs = conn.getPrinterAttributes(name)
        except Exception as e:
            logger.warning("Error al leer atributos de %s: %s", name, e)
            result["printers"][name] = {
                "ready": False,
                "estado": "not_ready",
                "estado_codigo": ESTADO_CODIGO_NOT_READY,
                "razon": "Error al leer atributos de la impresora",
                "detalles": [],
                "cups_state": None,
                "modelo": info.get("printer-make-and-model", "Desconocida"),
                "ocupada": False,
            }
            continue

        result["printers"][name] = _estado_desde_atributos(
            attrs, modelo_fallback=info.get("printer-make-and-model", "Genérica")
        )

    return result


def estado_impresora(nombre: str) -> dict[str, Any] | None:
    """
    Estado de una sola impresora por nombre.
    Retorna None si la impresora no existe.
    En modo mock respeta los datos de prueba (no devuelve None por _cups_unavailable).
    Consulta directa a CUPS por nombre para evitar O(n) de monitorear_flota().
    """
    if not CUPS_AVAILABLE:
        if _mock_impresoras_habilitado():
            return _respuesta_mock_flota().get("printers", {}).get(nombre)
        return None
    try:
        conn = cups.Connection()
        attrs = conn.getPrinterAttributes(nombre)
    except Exception as e:
        logger.warning("Error al consultar impresora %s: %s", nombre, e)
        if _mock_impresoras_habilitado():
            return _respuesta_mock_flota().get("printers", {}).get(nombre)
        return None
    if not attrs:
        if _mock_impresoras_habilitado():
            return _respuesta_mock_flota().get("printers", {}).get(nombre)
        return None
    return _estado_desde_atributos(attrs)


class CupsPrinterDiscoveryService(PrinterDiscovery):
    """Implementación de PrinterDiscovery usando CUPS."""

    def get_flota_status(self) -> dict[str, Any]:
        return monitorear_flota()

    def get_printer_status(self, name: str) -> dict[str, Any] | None:
        return estado_impresora(name)

    def discover_printers(self) -> list[dict[str, Any]]:
        """Lista impresoras descubiertas con nombre, modelo y tipo detectado."""
        flota = monitorear_flota()
        printers = flota.get("printers", {})
        
        result = []
        for name, info in printers.items():
            modelo = info.get("modelo", "Desconocida")
            tipo = _detectar_tipo_impresora(modelo)
            result.append({
                "name": name,
                "model": modelo,
                "type": tipo,
            })
        
        return result
