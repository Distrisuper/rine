"""
Render de etiquetas ZPL usando Jinja2.
Carga archivos .zpl del disco y reemplaza las variables {{ variable }}.
"""
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from domain.services.label_renderer_interface import LabelRenderer
from domain.value_objects import LabelRenderData

class ZplLabelRenderer(LabelRenderer):
    def __init__(self, templates_path: str):
        self.templates_path = templates_path
        self._env = Environment(
            loader=FileSystemLoader(templates_path),
            autoescape=select_autoescape()
        )

    def render(self, template_path: str, data: LabelRenderData) -> bytes:
        """
        template_path: nombre del archivo relativo a self.templates_path (ej: 'zebra_label.zpl')
        """
        # Extraer el nombre del archivo si viene con ruta completa
        file_name = os.path.basename(template_path)
        
        template = self._env.get_template(file_name)
        
        # Convertimos el ValueObject a dict para Jinja2
        context = {
            # "client_code": data.client_code,
            # "client_name": data.client_name,
            # "order_number": data.order_number,
            # "channel": data.channel,
            "to": data.to,
            "address": data.address,
            "city": data.city,
            "packages": data.packages
        }
        
        rendered_zpl = template.render(**context)
        return rendered_zpl
        # return rendered_zpl.encode("latin-1", errors="replace")
