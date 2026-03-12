from domain.services.document_builder.document_builder_interface import DocumentBuilder

class DocumentBuilderFactory:
    """Fábrica de builders de documentos según origen y tipo."""
    
    _label_builder = None
    _remito_builder = None
    _s3_fricrot_builder = None

    @classmethod
    def set_builders(cls, label_builder, remito_builder, s3_fricrot_builder):
        """Inyección de dependencias para la fábrica."""
        cls._label_builder = label_builder
        cls._remito_builder = remito_builder
        cls._s3_fricrot_builder = s3_fricrot_builder

    @classmethod
    def get_for(cls, channel, session=None) -> DocumentBuilder:
        # 1. Caso S3 (Remitos externos de Fric-Rot)
        if channel.document_source == "S3_REMITOS_FRIC_ROT":
            if not cls._s3_fricrot_builder:
                from domain.services.document_builder.s3_fricrot_remitos_builder import S3FricRotRemitosBuilder
                cls._s3_fricrot_builder = S3FricRotRemitosBuilder()
            return cls._s3_fricrot_builder

        # 2. Caso INTERNAL (Renderizado propio con Templates)
        if channel.document_source == "INTERNAL":
            if session is None:
                # Nota: Esto solo debería ocurrir si channel ya tiene cargado el template
                template = channel.template
            else:
                template = channel.get_template(session)
                
            if not template:
                raise ValueError(f"El canal {channel.channel_number} es 'INTERNAL' pero no tiene un template asociado.")

            file_path = template.file_path.lower()
            
            if file_path.endswith('.zpl'):
                if not cls._label_builder:
                    raise RuntimeError("LabelDocumentBuilder no inyectado en la fábrica.")
                return cls._label_builder
            
            if file_path.endswith('.html'):
                if not cls._remito_builder:
                    raise RuntimeError("RemitoDocumentBuilder no inyectado en la fábrica.")
                return cls._remito_builder

            raise ValueError(
                f"Para origen INTERNAL, el archivo '{file_path}' no es soportado. "
                "Debe ser .zpl o .html."
            )

        # 3. Caso no reconocido
        raise ValueError(
            f"Origen de documento '{channel.document_source}' no soportado por el sistema. "
            "Valores válidos: 'INTERNAL', 'S3_REMITOS_FRIC_ROT'."
        )
