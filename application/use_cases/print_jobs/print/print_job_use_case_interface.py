from abc import ABC, abstractmethod


class PrintJobUseCaseInterface(ABC):
    @abstractmethod
    def __call__(
        self,
        printer_name: str,
        content: bytes,
        content_type: str,
        job_title: str,
    ) -> int:
        pass
