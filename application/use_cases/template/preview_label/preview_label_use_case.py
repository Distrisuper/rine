import json
from sqlmodel import Session, select
from application.use_cases.template.preview_label.preview_label_use_case_interface import PreviewLabelUseCaseInterface
from domain.entities.print_job import PrintJob
from domain.entities.channel import Channel

class PreviewLabelUseCase(PreviewLabelUseCaseInterface):
    def __init__(self, session: Session):
        self._session = session

    def __call__(self, body) -> bytes:
        # 1. Validar que el canal sea para etiquetas (INTERNAL + .zpl)
        channel = self._session.exec(
            select(Channel).where(Channel.channel_number == body.channel)
        ).first()
        
        if not channel:
            raise ValueError(f"El canal {body.channel} no existe")
            
        template = channel.get_template(self._session)
        if not template or not template.file_path.lower().endswith('.zpl'):
            raise ValueError(f"El canal {body.channel} no está configurado con una plantilla de etiquetas (.zpl)")

        # 2. Instanciar un PrintJob transitorio
        job = PrintJob(
            client_code=body.client_code,
            client_name=body.client_name,
            channel=body.channel,
            payload=json.dumps(body.payload) if isinstance(body.payload, dict) else body.payload,
            number_of_copies=1
        )
        
        # 3. Renderizar usando la lógica de la entidad
        return job.render(self._session)
