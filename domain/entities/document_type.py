from dataclasses import dataclass


DOCUMENT_TYPES = {
    3: {"printer_key": "zebra_printer", "output_format": "zpl"},
    4: {"printer_key": "laser_printer", "output_format": "pdf"},
    8: {"printer_key": "laser_printer", "output_format": "pdf"},
}


def get_document_type(channel: int) -> dict:
    if channel not in DOCUMENT_TYPES:
        raise ValueError(f"Channel {channel} no soportado")
    return DOCUMENT_TYPES[channel]


def get_printer_key(channel: int) -> str:
    return get_document_type(channel)["printer_key"]


def get_output_format(channel: int) -> str:
    return get_document_type(channel)["output_format"]
