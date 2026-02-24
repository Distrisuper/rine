from fastapi import Response

from application.use_cases.template.render_remito.render_remito_use_case_interface import RenderRemitoUseCaseInterface


class RenderRemitoController:
    def __init__(self, use_case: RenderRemitoUseCaseInterface):
        self._use_case = use_case

    def __call__(self, body) -> Response:
        pdf_bytes = self._use_case(body)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="remito.pdf"'},
        )
