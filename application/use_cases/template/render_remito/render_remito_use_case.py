from render_remito_use_case_interface import RenderRemitoUseCaseInterface


class RenderRemitoUseCase(RenderRemitoUseCaseInterface):
    def __init__(self, template_service):
        self._template_service = template_service

    def __call__(self, body) -> bytes:
        item = body.to_queue_item()
        return self._template_service.render(item)
