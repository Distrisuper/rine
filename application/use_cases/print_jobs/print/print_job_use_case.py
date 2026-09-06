from application.use_cases.print_jobs.print.print_job_use_case_interface import (
    PrintJobUseCaseInterface,
)
from infrastructure.services.print_job_service import print_pdf_to_printer, print_raw_to_printer


class PrintJobUseCase(PrintJobUseCaseInterface):
    def __call__(
        self,
        printer_name: str,
        content: bytes,
        content_type: str,
        job_title: str,
        number_of_copies: int = 1,
        print_job_id: int | None = None,
    ) -> int:
        if content_type == "pdf":
            return print_pdf_to_printer(
                printer_name,
                content,
                job_title,
                number_of_copies,
                print_job_id=print_job_id,
            )
        return print_raw_to_printer(
            printer_name,
            content,
            job_title,
            number_of_copies,
            print_job_id=print_job_id,
        )
