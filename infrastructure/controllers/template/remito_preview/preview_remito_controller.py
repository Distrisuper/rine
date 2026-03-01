import base64
from fastapi import Response
from fastapi.responses import JSONResponse
from application.use_cases.template.preview_remito.preview_remito_use_case_interface import PreviewRemitoUseCaseInterface
from infrastructure.dtos.template.remito_preview.request import RemitoPreviewRequestDTO

class PreviewRemitoController:
    def __init__(self, use_case: PreviewRemitoUseCaseInterface):
        self._use_case = use_case

    def __call__(self, body: RemitoPreviewRequestDTO, format: str = "binary"):
        pdf_bytes = self._use_case(body)
        
        if format == "json":
            return JSONResponse(content={
                "content_type": "application/pdf",
                "size": len(pdf_bytes),
                "content_base64": base64.b64encode(pdf_bytes).decode("ascii"),
            })
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="remito.pdf"'},
        )
