from functools import lru_cache

from application.use_cases.channels.create.create_channel_use_case import CreateChannelUseCase
from application.use_cases.hello.get.get_hello_use_case import GetHelloUseCase
from application.use_cases.health.health_use_case import HealthUseCase
from application.use_cases.print_jobs.create.create_print_job_use_case import CreatePrintJobUseCase
from application.use_cases.print_jobs.print.print_job_use_case import PrintJobUseCase
from application.use_cases.printer.discover.discover_printer_use_case import DiscoverPrinterUseCase
from application.use_cases.printer.get_one_status_by_name.get_one_status_by_name_use_case import GetOneStatusByNameUseCase
from application.use_cases.printer.get_status.get_status_use_case import GetStatusUseCase
from application.use_cases.template.render_label.render_label_use_case import RenderLabelUseCase
from infrastructure.controllers.printer.discover.discover_printer_controller import DiscoverPrinterController
from infrastructure.controllers.printer.get_one_status_by_name.get_one_status_by_name_controller import GetOneStatusByNameController
from infrastructure.controllers.printer.get_status.get_status_controller import GetStatusController
from infrastructure.controllers.template.label_preview.label_preview_controller import LabelPreviewController
from infrastructure.services.printer_discovery_service import CupsPrinterDiscoveryService


class Container:
    # Hello
    @lru_cache
    def init_hello_controller(self) -> HelloGetController:
        use_case = GetHelloUseCase()
        return HelloGetController(use_case)

    def hello_controller(self) -> HelloGetController:
        return self.init_hello_controller()

    # Health
    @lru_cache
    def init_health_controller(self) -> HealthController:
        use_case = HealthUseCase()
        return HealthController(use_case)

    def health_controller(self) -> HealthController:
        return self.init_health_controller()

    # Channel
    @lru_cache
    def init_create_channel_controller(self) -> CreateChannelController:
        use_case = CreateChannelUseCase()
        return CreateChannelController(use_case)

    def create_channel_controller(self) -> CreateChannelController:
        return self.init_create_channel_controller()

    # PrintJob
    @lru_cache
    def init_create_print_job_controller(self) -> CreatePrintJobController:
        use_case = CreatePrintJobUseCase()
        return CreatePrintJobController(use_case)

    def create_print_job_controller(self) -> CreatePrintJobController:
        return self.init_create_print_job_controller()

    # Print
    @lru_cache
    def init_print_job_controller(self) -> PrintJobController:
        use_case = PrintJobUseCase()
        return PrintJobController(use_case)

    def print_job_controller(self) -> PrintJobController:
        return self.init_print_job_controller()

    # Printer - Discover
    @lru_cache
    def init_discover_printer_controller(self) -> DiscoverPrinterController:
        discovery = CupsPrinterDiscoveryService()
        use_case = DiscoverPrinterUseCase(discovery)
        return DiscoverPrinterController(use_case)

    def discover_printer_controller(self) -> DiscoverPrinterController:
        return self.init_discover_printer_controller()

    # Printer - Get One Status By Name
    @lru_cache
    def init_get_one_status_by_name_controller(self) -> GetOneStatusByNameController:
        discovery = CupsPrinterDiscoveryService()
        use_case = GetOneStatusByNameUseCase(discovery)
        return GetOneStatusByNameController(use_case)

    def get_one_status_by_name_controller(self) -> GetOneStatusByNameController:
        return self.init_get_one_status_by_name_controller()

    # Printer - Get Status
    @lru_cache
    def init_get_status_controller(self) -> GetStatusController:
        discovery = CupsPrinterDiscoveryService()
        use_case = GetStatusUseCase(discovery)
        return GetStatusController(use_case)

    def get_status_controller(self) -> GetStatusController:
        return self.init_get_status_controller()

    # Template - Label Preview
    @lru_cache
    def init_label_preview_controller(self) -> LabelPreviewController:
        from domain.services.label_template_service import LabelTemplateService
        template_service = LabelTemplateService()
        use_case = RenderLabelUseCase(template_service)
        return LabelPreviewController(use_case)

    def label_preview_controller(self) -> LabelPreviewController:
        return self.init_label_preview_controller()


container = Container()
