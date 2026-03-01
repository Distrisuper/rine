from typing import Optional
from application.use_cases.channels.update.update_channel_use_case_interface import UpdateChannelUseCaseInterface

class UpdateChannelController:
    def __init__(self, use_case: UpdateChannelUseCaseInterface):
        self._use_case = use_case

    def __call__(self, channel_id: int, description: Optional[str], is_active: Optional[bool], template_id: Optional[int]) -> dict:
        return self._use_case(channel_id, description, is_active, template_id)
