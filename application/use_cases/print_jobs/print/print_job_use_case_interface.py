from abc import ABC, abstractmethod


class PrintJobUseCaseInterface(ABC):
    @abstractmethod
    def __call__(
        self,
        printer_name: str,
        content: bytes,
        content_type: str,
        job_title: str,
        number_of_copies: int = 1,
        print_job_id: int | None = None,
    ) -> int:
        pass
