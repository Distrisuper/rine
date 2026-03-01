import base64

from fastapi import Response
from fastapi.responses import JSONResponse

from application.use_cases.template.preview_label.preview_label_use_case_interface import PreviewLabelUseCaseInterface
from infrastructure.dtos.template.label_preview.request import LabelPreviewRequestDTO


class PreviewLabelController:
    def __init__(self, use_case: PreviewLabelUseCaseInterface):
        self._use_case = use_case

    def __call__(self, body: LabelPreviewRequestDTO, format: str = "binary"):
        zpl_bytes = self._use_case(body)
        
        if format == "json":
            return JSONResponse(content={
                "content_type": "application/vnd.zpl",
                "size": len(zpl_bytes),
                "content_base64": base64.b64encode(zpl_bytes).decode("ascii"),
                "content_preview": zpl_bytes.decode("utf-8", errors="replace")[:500],
            })
        
        return Response(content=zpl_bytes, media_type="application/vnd.zpl")
