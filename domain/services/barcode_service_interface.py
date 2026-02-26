from abc import ABC, abstractmethod


class BarcodeServiceInterface(ABC):
    @abstractmethod
    def to_svg_data_url(self, value: str) -> str | None:
        pass
