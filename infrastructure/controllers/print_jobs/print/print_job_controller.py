from application.use_cases.print_jobs.print.print_job_use_case_interface import (
    PrintJobUseCaseInterface,
)


class PrintJobController:
    def __init__(self, use_case: PrintJobUseCaseInterface):
        self._use_case = use_case

    def __call__(self, printer_name: str, content: bytes, content_type: str, job_title: str) -> int:
        return self._use_case(
            printer_name=printer_name,
            content=content,
            content_type=content_type,
            job_title=job_title,
        )
