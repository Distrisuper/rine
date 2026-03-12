import base64

from fastapi import Response
from fastapi.responses import JSONResponse

from application.use_cases.template.preview_label.preview_label_use_case_interface import PreviewLabelUseCaseInterface
from infrastructure.dtos.template.label_preview.request import LabelPreviewRequestDTO


class PreviewLabelController:
    def __init__(self, use_case: PreviewLabelUseCaseInterface):
        self._use_case = use_case

    def __call__(self, body: LabelPreviewRequestDTO, format: str = "binary"):
        # El caso de uso ahora devuelve un RenderedDocument
        result = self._use_case(body)
        
        if format == "json":
            return JSONResponse(content={
                "content_type": f"application/vnd.{result.content_type}",
                "size": len(result.content),
                "content_base64": base64.b64encode(result.content).decode("ascii"),
                "content_preview": result.content.decode("utf-8", errors="replace")[:500],
            })
        
        return Response(
            content=result.content, 
            media_type=f"application/vnd.{result.content_type}"
        )
