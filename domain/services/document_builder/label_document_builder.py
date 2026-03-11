from sqlmodel import Session
from domain.services.document_builder.document_builder_interface import DocumentBuilder
from domain.value_objects.rendered_document import RenderedDocument

class LabelDocumentBuilder(DocumentBuilder):
    """Estrategia para construir etiquetas ZPL."""

    def __init__(self, renderer):
        self._renderer = renderer

    def build(self, job, session: Session) -> RenderedDocument:
        template = job.get_template(session)
        if not template:
            raise ValueError(f"No hay template para el channel {job.channel}")
            
        data = job.get_render_data_label()
        content = self._renderer.render(template.file_path, data)
        
        return RenderedDocument(
            content=content,
            content_type="zpl",
            title="Etiqueta"
        )
