from application.use_cases.channels.create.create_channel_use_case_interface import (
    CreateChannelUseCaseInterface,
)


class CreateChannelController:
    def __init__(self, use_case: CreateChannelUseCaseInterface):
        self._use_case = use_case

    def __call__(self, channel_number: int, document_source: str, description: str | None = None, template_id: int | None = None) -> dict:
        return self._use_case(
            channel_number=channel_number,
            description=description,
            template_id=template_id,
            document_source=document_source,
        )
