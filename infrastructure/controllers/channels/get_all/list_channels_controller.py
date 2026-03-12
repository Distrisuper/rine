from application.use_cases.channels.get_all.list_channels_use_case_interface import ListChannelsUseCaseInterface

class ListChannelsController:
    def __init__(self, use_case: ListChannelsUseCaseInterface):
        self._use_case = use_case

    def __call__(self) -> list:
        return self._use_case()
