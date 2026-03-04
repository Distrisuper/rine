from typing import Optional
from application.use_cases.channels.update.update_channel_use_case_interface import UpdateChannelUseCaseInterface

class UpdateChannelController:
    def __init__(self, use_case: UpdateChannelUseCaseInterface):
        self._use_case = use_case

    def __call__(self, channel_id: int, description: Optional[str] = None, is_active: Optional[bool] = None, template_id: Optional[int] = None, document_source: Optional[str] = None) -> dict:
        return self._use_case(channel_id, description, is_active, template_id, document_source)
