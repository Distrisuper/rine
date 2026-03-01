from application.use_cases.template.render_remito.render_remito_use_case_interface import RenderRemitoUseCaseInterface


class RenderRemitoUseCase(RenderRemitoUseCaseInterface):
    def __init__(self, template_service):
        self._template_service = template_service

    def __call__(self, body) -> bytes:
        if body.channel not in (4, 8):
            raise ValueError("Solo se soporta channel=4 u 8 para remitos")
        
        item = body.to_queue_item()
        return self._template_service.render(item)
