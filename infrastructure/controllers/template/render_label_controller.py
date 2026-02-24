from fastapi import Response

from application.use_cases.template.render_label.render_label_use_case_interface import RenderLabelUseCaseInterface


class RenderLabelController:
    def __init__(self, use_case: RenderLabelUseCaseInterface):
        self._use_case = use_case

    def __call__(self, body) -> Response:
        zpl_bytes = self._use_case(body)
        return Response(content=zpl_bytes, media_type="application/vnd.zpl")
