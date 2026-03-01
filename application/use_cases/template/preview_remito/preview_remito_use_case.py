from application.use_cases.template.preview_remito.preview_remito_use_case_interface import PreviewRemitoUseCaseInterface

class PreviewRemitoUseCase(PreviewRemitoUseCaseInterface):
    def __call__(self, data):
        # Lógica para manejar la vista previa del remito
        return {"message": "Vista previa del remito generada con éxito."}