import base64
from fastapi import Response
from fastapi.responses import JSONResponse
from application.use_cases.template.preview_remito.preview_remito_use_case_interface import PreviewRemitoUseCaseInterface
from infrastructure.dtos.template.remito_preview.request import RemitoPreviewRequestDTO

class PreviewRemitoController:
    def __init__(self, use_case: PreviewRemitoUseCaseInterface):
        self._use_case = use_case

    def __call__(self, body: RemitoPreviewRequestDTO, format: str = "binary"):
        # El caso de uso ahora devuelve un RenderedDocument
        result = self._use_case(body)
        
        if format == "json":
            return JSONResponse(content={
                "content_type": "application/pdf",
                "size": len(result.content),
                "content_base64": base64.b64encode(result.content).decode("ascii"),
            })
        
        return Response(
            content=result.content,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="remito.pdf"'},
        )
