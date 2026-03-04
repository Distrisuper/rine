from domain.services.document_builder.document_builder_interface import DocumentBuilder
from domain.services.document_builder.template_document_builder import TemplateDocumentBuilder


class DocumentBuilderFactory:
    @staticmethod
    def get_for(channel) -> DocumentBuilder:
        if channel.document_source == "S3_REMITOS_FRIC_ROT":
            from domain.services.document_builder.s3_fricrot_remitos_builder import S3FricRotRemitosBuilder
            return S3FricRotRemitosBuilder()
        return TemplateDocumentBuilder()
