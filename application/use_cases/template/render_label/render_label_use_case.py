from application.use_cases.template.render_label.render_label_use_case_interface import RenderLabelUseCaseInterface


class RenderLabelUseCase(RenderLabelUseCaseInterface):
    def __init__(self, template_service):
        self._template_service = template_service

    def __call__(self, body) -> bytes:
        if body.channel != 3:
            raise ValueError("Solo se soporta channel=3 para etiquetas")
        
        item = body.to_queue_item()
        return self._template_service.render(item)
