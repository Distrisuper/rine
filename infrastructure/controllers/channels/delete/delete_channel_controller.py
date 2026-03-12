from application.use_cases.channels.delete.delete_channel_use_case_interface import DeleteChannelUseCaseInterface

class DeleteChannelController:
    def __init__(self, use_case: DeleteChannelUseCaseInterface):
        self._use_case = use_case

    def __call__(self, channel_id: int) -> dict:
        self._use_case(channel_id)
        return {
            "status": "deleted",
            "id": channel_id
        }
