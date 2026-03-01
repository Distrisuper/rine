from application.use_cases.channels.delete.delete_channel_use_case_interface import DeleteChannelUseCaseInterface
from domain.repositories.channel_repository import ChannelRepository

class DeleteChannelUseCase(DeleteChannelUseCaseInterface):
    def __init__(self, repo: ChannelRepository):
        self._repo = repo

    def __call__(self, channel_id: int) -> bool:
        return self._repo.delete(channel_id)
